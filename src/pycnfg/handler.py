"""
The :class:`pycnfg.Handler` contains class to read and execute configuration.

The purpose of any configuration is to produced result (object) by combining
resources (steps). Pycnfg offers unified patten to create arbitrary Python
objects pipeline-wise. That naturally allows to control all parameters via
single configuration.

Configuration is a python dictionary. It supports multiple sections. Each
section specify set of sub-configurations. Each sub-configuration provide steps
to construct an object, that can be utilize as argument in other sections.
Whole configuration could be passed to :class:`pycnfg.run` or to user-defined
wrapper around :class:`pycnfg.Handler`, that builds target sub-configurations
objects one by one.

For each section there is common logic:

.. code-block::

    {'section_id':
        'configuration_id 1': {
            'init': Initial object state.
            'producer': Factory class, contained methods to run steps.
            'patch': Add custom methods to class.
            'steps': [
                ('method_id 1', {'kwarg_id': value, ..}),
                ('method_id 2', {'kwarg_id': value, ..}),
            ],
            'global': Shortcut to common parameters.
            'priority': Execution priority (integer).
        }
        'configuration_id 2':{
            ...
        }
    }

The target for each sub-configuration is to create an object.
``init`` is the template for future object (for example empty dict).
``producer`` works as factory, it should contain ``produce()`` method that:
takes ``init`` and consecutive pass it and kwargs to ``steps`` methods and
returns resulting object.

.. code-block::

    # pseudocode
    def produce(self, init, steps):
        obj = init
        for step in steps:
            obj = decorators(getattr(self, step_id))(obj, objects, **kwargs)
        return obj

That object will be store in ``objects`` and can be used as kwargs for any
step in others sections.

.. code-block::

    objects['section_id__conf_id'] = obj

To specify the order in which sections handled, the ``priority`` key is
available in each sub-configuration.

For flexibility, it is possible:

* Specify default configuration for section(s).
* Specify global value for common kwargs in steps via ``global`` key.
* Create separate section for arbitrary parameter in steps.
* Monkey-patch ``producer`` object with custom functions via ``patch`` key.
* Set ``init`` as an instance, a class or a function
* Set decorators for any step.

Configuration keys
------------------

init : callable or instance, optional (default={})
    Initial state for constructing object. Will be passed consecutive in steps
    as argument. If set as callable ``init``(), auto called.

producer : class, optional (default=pycnfg.Producer)
    The factory to construct an object: ``producer.produce(init,steps)``.
    Class auto initialized: ``producer(objects, 'section_id__configuration_id',
    **kwargs)``, where ``objects`` is a dictionary with previously created
    objects {``section_id__configuration_id``: object}. If ('__init__', kwargs)
    step provided in ``steps``, kwargs will be passed to initializer.

patch : dict {'method_id' : function}, optional (default={})
    Monkey-patching the ``producer`` object with custom functions.

steps : list of tuples, optional (default=[])
    List of ``producer`` methods with kwargs to run consecutive.
    Each step should be a tuple: ``('method_id', kwargs, decorators)``,
    where 'method_id' should match to ``producer`` functions' names.
    In case of omitting any kwargs step executed with default, set in
    corresponding producer method.

    kwargs : dict, optional (default={})
        Step arguments: {'kwarg': value, ...}.

        It is possible to create separate section for any argument.
        Set ``section_id__configuration_id`` as kwarg value, then it would be
        auto-filled with corresponding object from ``objects`` storage before
        step execution. List of ``section_id__configuration_id`` is also
        possible. To prevent auto substitution, set special '_id' postfix
        ``kwarg_id``.

        It`is possible to turn on resolving ``None`` values for explicitly set
        kwargs in ``steps``. See ``resolve_none`` argument in :func:`pycnfg.
        Handler.read` :
        If `value` is set to None, parser try to resolve it. First searches for
        value in sub-cconfiguration ``global``. Then resolver looks up 'kwarg'
        in section names.
        If such section exist, there are two possibilities:
        if 'kwarg' name contains '_id' postfix, resolver substitutes None with
        available ``section_id__configuration_id``, otherwise with
        configuration object.
        If fails to find resolution, ``value`` is remained None. In case of
        resolution plurality, ValueError is raised.

    decorators: list, optional (default=[])
        Step decorators from most inner to outer: [decorator,]

priority : non-negative integer, optional (default=1)
    Priority of configuration execution. The more the higher priority.
    For two conf with same priority order is not guaranteed.
    If zero, not execute configuration.

global : dict , optional (default={})
    Specify values to substitute for any kwargs: ``{'kwarg_name': value, }``.
    It has priority over already set values in ``steps``. This is convenient
    for example when the same kwarg used in all methods or need to slightly
    adjust  default configuration. For the last case it is possible to specify
    more targeted path: ``{'step_id__kwarg_name': value, }``. If global
    contains multiple resolutions for some kwarg, targeted path has priority.

**keys : dict {'kwarg_name': value, ...}, optional (default={})
    All additional keys in configuration are moving to ``global`` automatically
    (rewrites already existed keys from the sub-conf level).

Notes
-----
Any configuration key above could be set in the most outer configuration level
or section level to specify common values either for all sections or all
sub-sections in some section (Examples below). The more inner level has
the higher priority, levels priority in ascending: ``conf level (0) => section
level (1) => sub-conf level (2)``. Supported keys: ``global, init, producer,
patch, steps, priority``.

- ``global`` keys from levels are merged according to level priorities.
Targeted path also possible, in priority:

    * ``section_id__conf_id__step_id__kwarg_name`` on level 0.
    * ``section_id__step_id__kwarg_name`` on level 0.
    * ``section_id__conf_id__kwarg_name`` on level 0.
    * ``section_id__kwarg_name`` on level 0.
    * ``conf_id__step_id__kwarg_name`` on levels 0,1.
    * ``conf_id__kwarg_name`` on levels 0,1.
    * ``step_id__kwarg_name`` on levels 0,1,2.
    * ``kwarg_name`` on levels 0,1,2.
On the same level "more" targeted path priority > non-targeted.

- other keys` value are replaced in level priority.

``section_id``/``configuration_id``/``step_id``/``kwargs_id`` should not
contain double underscore '__' (except magic methods in ``step_id``).

Default configurations can be set in :func:`pycnfg.Handler.read` ``dcnfg``
argument. Arbitrary objects could be pre-accommodated ``objects`` argument in
:func:`pycnfg.Handler.exec` , so no need to specify configurations for them.
If any provided it has priority over sub-configuration with the same id.

To add functionality to producer use ``patch`` key or inheritance from
:class:`pycnfg.Producer` .

Examples
--------
Patching producer with custom function.

.. code-block::

    def my_func(self, key, val):
        # ... custom logic ...
        return res

    CNFG = {..{'patch': {'func': my_func,},}}

``global`` on the most outer level to set kwargs in 'func' step and ``patch``
to add functionality. Section level ``init`` to set in both configuration
simultaneously:

.. code-block::

    CNFG = {

            'global': {
                'section_1__set__val': 42,
                'val': 99,
                },
            'patch': {'func': my_func},
            'section_1': {
                'init': {'a': 7},
                'conf_1': {
                    'steps': [
                        ('func', {'key': 'b', 'val': 24},),
                    ],
                },
                'conf_2': {
                    'steps': [
                        ('func', {'key': 'b', 'val': 24},),
                    ],
                },
            },
    }
    # Result:
    {
        'section_1__conf_1': {'a': 7, 'b': 42},
        'section_1__conf_2': {'a': 7, 'b': 99},
    }

There are two ways to set second level kwargs for some step,
for example kwarg 'c' for step 'func':

.. code-block::

    def func(a, b=7, **kwargs):
        print(kwargs['c'])

    # **kwargs could be set:
    # Implicitly via 'global'.
    CNFG = {..{
        'global': {'kwargs':{'c': 3}}
        'steps': [('func', {'a': 1)],
        }}
    # Explicitly in 'steps' (only if no 'c' in the first level).
    CNFG = {..{
        'steps': [('func', {'a': 1, 'c': 3)],
        }}
    # In the last case, 'global' can address 'c' directly:
    # 'global': {'c': 4}

See more detailed examples in :doc:`Examples <Examples>`  .

See Also
--------
:class:`pycnfg.Handler`: Read configurations, execute steps.

:data:`pycnfg.CNFG`: Default configurations.


"""


import collections
import copy
import functools
import heapq
import importlib.util
import inspect
import itertools
import operator
import sys
import time
import types

import pycnfg

__all__ = ['Handler']


class Handler(object):
    """Read and execute configurations.

    Interface: read, exec.

    See Also
    ---------
    :class:`pycnfg.Producer`: Execute configuration steps.

    """
    _required_parameters = []

    def __init__(self):
        # Save readed files as s under unique id.
        self._readed = {}
        self._dkeys = {
            'init': {},
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        }

    def read(self, cnfg, dcnfg=None, resolve_none=False):
        """Read raw configuration and transform to executable.

        Parameters
        ----------
        cnfg : dict or str
            Set of configurations:
            {'section_id': {'configuration_id': configuration,},}.
            If str, absolute path to file with ``CNFG`` variable.
        dcnfg : dict, str, optional (default=None)
            Set of default configurations:
            {'section_id': {'configuration_id': configuration, },}.
            If str, absolute path to file with ``CNFG`` variable.
            If None, use :data:`pycnfg.CNFG` .
        resolve_none : bool, optional (default=False)
            If True, try to resolve None values for step kwargs. If kwarg name
            matches with section name, substitute either with conf_id on zero
            position or val, depending on if ``_id`` prefix in ``kwarg_name``.

        Returns
        -------
        configs : list of tuple [('section_id__configuration_id', config),.].
            List of configurations, prepared for execution.

        Notes
        -----
        Apply default configuration ``dcnfg``:

        * Copy default sections that not in conf.
        * If sub-keys in some section`s sub-configuration are skipped:
         Try to find match ``section_id__configuration_id`` in default, if
         can`t copy from zero position sub-configuration. If default  section
         not exist at all, use default values for sub-keys: ``{'init': {},
         'priority': 1, 'class': pycnfg.Producer, 'global': {}, 'patch': {},
         'steps': [],}``.
        => skipped subkeys from 'global' key for most outer and section default
        levels will be also copy.

        Resolve None:

        * If any step kwarg is None => use value from ``global``.
        * If not in ``global`` => search 'kwarg_id' in 'section_id's.

            * If no section => remain None.
            * If section exist:
             If more then one configurations in section => ValueError.
             If 'kwarg_id' contains postfix '_id', substitute None with
             ``section_id__configuration_id``, otherwise with object.

        """
        if dcnfg is None:
            dcnfg = copy.deepcopy(pycnfg.CNFG)

        if isinstance(cnfg, str):
            cnfg = self._import_cnfg(cnfg)
        if isinstance(dcnfg, str):
            dcnfg = self._import_cnfg(dcnfg)
        configs = self._parse_cnfg(cnfg, dcnfg, resolve_none)
        return configs

    def _import_cnfg(self, conf):
        """Read file as module, get CNFG."""
        conf_id = str(time.time())
        spec = importlib.util.spec_from_file_location(f'CNFG_{conf_id}',
                                                      f"{conf}")
        conf_file = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conf_file)
        # Otherwise problem with CNFG pickle, depends on the module path.
        sys.modules[f'CNFG_{conf_id}'] = conf_file
        with open(conf, 'r') as f:
            self._readed[conf_id] = f.read()
        conf = copy.deepcopy(conf_file.CNFG)
        return conf

    def exec(self, configs, objects=None, debug=False):
        """Execute configurations in priority.

        For each configuration:

        * Initialize producer
         ``producer(objects,``section_id__configuration_id``, **kwargs)``,
         where kwargs taken from ('__init__', kwargs) step if provided.
        * call ``producer.produce(init, steps)``.
        * store result under ``section_id__configuration_id`` in ``objects``.

        Parameters
        ----------
        configs : list of tuple
            List of configurations, prepared for execution:
            [('section_id__config__id', config), ...]
        objects : dict, optional (default=None)
            Dict of initial objects. If None, {}.
        debug : bool
            If True, print debug information.

        Returns
        -------
        objects : dict
            Dictionary with resulted objects from ``configs`` execution"
            {'section_id__config__id': object}

        Notes
        -----
        ``producer``/``init`` auto initialized if needed.

        """
        if objects is None:
            objects = {}

        for config in configs:
            if debug:
                print(config, flush=True)
            oid, val = config
            if oid in objects:
                print(f"Warninig: Identifier '{oid}' is already in "
                      f"'objects', original object remains.", flush=True)
                continue
            objects[oid] = self._exec(oid, val, objects)
        return objects

    def _parse_cnfg(self, p, dp, resolve_none):
        # Apply default.
        p = self._merge_default(p, dp)
        # Resolve global / None.
        p = self._resolve(p, resolve_none)
        # Arrange in priority.
        res = self._priority_arrange(p)  # [('section_id__config__id', config)]
        self._check_res(res)
        return res

    def _merge_default(self, p, dp):
        """Add skipped key from default.

        * copy from dp cnfg level and section levels 'global' if not exist,
        otherwise ignore.
        * Copy skipped sections from dp (could be multiple confs).
        * Copy skipped sub-keys from dp section(s) of the same name.
         If dp section contains multiple confs, search for nmae match,
         otherwise use zero position conf.
        * Fill skipped sub-keys for section not existed in dp.
         {'init': {}, 'class': pycnfg.Producer, 'global': {}, 'patch': {},
         'priority': 1, 'steps': [],}
        * Fill skipped steps {kwargs:{}, decorators:[]}
        * Add special 'global' to conf level and section levels.
        """
        dkeys = self._dkeys

        for section_id in dp:
            if section_id not in p:
                # Copy skipped section_ids from dp.
                p[section_id] = copy.deepcopy(dp[section_id])
            # [deprecated] disable merge, bad logic.
            # elif section_id is 'global':
            #     # merge and copy.
            #     tmp = copy.deepcopy(dp[section_id])
            #     tmp.update(p[section_id])
            #     p[section_id] = tmp
            else:
                # Copy skipped sub-keys for existed in dp conf (zero position
                # or name match). Also work for 'global' on section level,
                # not overwrite existed.
                dp_conf_ids = list(dp[section_id].keys())
                # [deprecated] disable merge, bad logic.
                # if 'global' not in p[section_id]:
                #     # Otherwise would not sync section level global.
                #     p[section_id]['global'] = {}
                for conf_id, conf in p[section_id].items():
                    if conf_id in dkeys:
                        continue
                    if conf_id in dp[section_id]:
                        dp_conf_id = conf_id
                    # [deprecated] disable merge, bad logic.
                    # elif conf_id is 'global':
                    #    continue
                    else:
                        # Get zero position dp conf in section.
                        dp_conf_id = dp_conf_ids[0]
                    for subkey in dp[section_id][dp_conf_id].keys():
                        if subkey not in conf:
                            conf[subkey] = copy.deepcopy(
                                dp[section_id][dp_conf_id][subkey])
                # Copy dkeys section level from dp if no exist in p.
                for conf_id, conf in dp[section_id].items():
                    if conf_id in dkeys and conf_id not in p[section_id]:
                        p[section_id][conf_id] = copy.deepcopy(conf)
        return p

    # [future]
    def _find_new_keys(self, p, dp):
        """Find keys that not exist in dp."""
        new_keys = set()
        for key in list(p.keys()):
            if key not in dp:
                new_keys.add(key)
        if new_keys:
            # user can create configuration for arbitrary param
            # check if dict type
            for key in new_keys:
                if not isinstance(p[key], dict):
                    raise TypeError(f"Custom params[{key}]"
                                    f" should be the dict instance.")

    def _resolve(self, p, resolve_none):
        """Resolve and substitute dkeys and None inplace."""
        # ``unused_nonglobal`` contain unused non-global dkeys to log.
        unused_nonglobal = set()  # {'level_2__producer',..}
        # ``unused_global`` contain unused global to log.
        unused_global = set()  # {'level_2__section__conf__kwarg_id',..}
        # ``used_ids`` contain used conf_ids ref by each section [future].
        used_ids = {}  # {'section_id': set('configuration_id', )}
        self._resolve_nonglobal(p, unused_nonglobal)
        self._resolve_global(p, unused_global)
        for section_id in p.keys()-self._dkeys.keys():
            for conf_id in p[section_id].keys()-self._dkeys.keys():
                self._substitute_global(section_id, conf_id,
                                        p[section_id][conf_id], unused_global)
                if resolve_none:
                    self._resolve_none(p, section_id, conf_id, used_ids)
        if unused_nonglobal or unused_global:
            print(f"Warning: Unused global key(s):\n"
                  f"    {unused_nonglobal|unused_global}", flush=True)
        return p

    def _resolve_nonglobal(self, p, unused):
        """Resolve dkeys (except global) and substitute.

        For each sub-conf resolve dkeys in priority:
            sub-conf => section => conf => default dkey.
        Delete outer levels in the end.

        """
        dkeys = self._dkeys
        used = set()
        for section_id in p.keys()-dkeys.keys():
            # Add dkeys (in dp also could not be necessary full set).
            for conf_id, conf in p[section_id].items():
                if conf_id in dkeys:
                    continue
                for dkey in dkeys.keys()-{'global'}:
                    if dkey in conf:
                        continue
                    elif dkey in p[section_id]:
                        conf[dkey] = copy.deepcopy(p[section_id][dkey])
                        used.add(f"level_1__{dkey}")
                    elif dkey in p:
                        conf[dkey] = copy.deepcopy(p[dkey])
                        used.add(f"level_0__{dkey}")
                    else:
                        # Alternative is to pre-set in level_0.
                        conf[dkey] = copy.deepcopy(dkeys[dkey])
            # Add empty kwargs/decorator to 'steps' (including __init__).
            for conf_id, conf in p[section_id].items():
                if conf_id in dkeys:
                    continue
                for i, step in enumerate(conf['steps']):
                    if not isinstance(step[0], str):
                        raise TypeError(f"step[0] should be a str:\n"
                                        f"    {section_id}__{conf_id}")
                    if len(step) > 1:
                        if not isinstance(step[1], dict):
                            raise TypeError(f"step[1] should be a dict:\n"
                                            f"    {section_id}__{conf_id}:"
                                            f" {step[0]}")
                    else:
                        conf['steps'][i] = (step[0], {}, [])
                        continue
                    if len(step) > 2:
                        if not isinstance(step[2], list):
                            raise TypeError(f"On step[2] should be a list:\n"
                                            f"    {section_id}__{conf_id}:"
                                            f" {step[0]}")
                    else:
                        conf['steps'][i] = (step[0], step[1], [])
        # Remove outer dkeys (except global).
        for dkey in dkeys.keys()-{'global'}:
            if dkey in p:
                del p[dkey]
                dkey_id = f"level_0__{dkey}"
                if dkey_id not in used:
                    unused.add(dkey_id)
            for section_id in list(p.keys() - dkeys.keys()):
                if dkey in p[section_id]:
                    del p[section_id][dkey]
                    dkey_id = f"level_1__{dkey}"
                    if dkey_id not in used:
                        unused.add(dkey_id)
        return

    def _resolve_global(self, p, unused):
        """Resolve global key.

        For each global level, add level prefix and merge to inner level.
        Ascending 'global' level priority: conf => section => sub-conf.
        Targeted path has priority in each level in case of plurality.

        """
        # Sub-configuration level, assemble unknown keys to global
        # (should be before copy from section).
        dkeys = self._dkeys
        for section_id in p.keys()-dkeys.keys():
            for conf_id in p[section_id].keys()-dkeys.keys():
                found = dict()
                for key in list(p[section_id][conf_id].keys()):
                    if key not in ['init', 'producer', 'global',
                                   'patch', 'steps', 'priority']:
                        found.update({key: p[section_id][conf_id].pop(key)})
                if 'global' not in p[section_id][conf_id]:
                    p[section_id][conf_id]['global'] = {}
                p[section_id][conf_id]['global'].update(found)

        # Configuration level, copy to section.
        self._copy_global(p, 0)

        # Section level, copy to global.
        for section_id in p.keys() - dkeys.keys():
            self._copy_global(p[section_id], 1)

        # Form set of all global keys (remove used on substitute).
        for section_id in p.keys()-dkeys.keys():
            for conf_id in p[section_id].keys()-dkeys.keys():
                # Add level prefix on conf global.
                glob = p[section_id][conf_id]['global']
                for i in list(glob.keys()):
                    if 'level_' not in i:
                        glob[f"level_{2}__{i}"] = glob.pop(i)
                # Add all to storage.
                unused.update(p[section_id][conf_id]['global'])
        return

    def _copy_global(self, p, level):
        """Merge global to inner level.

        Parameters
        ----------
        p: dict
            config on current level.
        level: int
            0 - most outer, 1 - section , 2 - config.

        """
        if 'global' not in p:
            return
        dkeys = self._dkeys
        glob = p['global']
        # Add level if not already:
        for i in list(glob.keys()):
            if 'level_' not in i:
                glob[f"level_{level}__{i}"] = glob.pop(i)
        # Others copy to all subsection.
        for i in glob:
            for subsection_id in p.keys()-dkeys.keys():
                if 'global' not in p[subsection_id]:
                    p[subsection_id]['global'] = {}
                p[subsection_id]['global'] = {i: copy.deepcopy(glob[i]),
                                              **p[subsection_id]['global']}
        # Delete level global (will remains only last).
        del p['global']
        return

    def _substitute_global(self, section_id, conf_id, conf, unused):
        """Substitute sub-configuration globals.

        Notes
        -----
            Inner level has higher priority than outer.
            On each level targeted path has higher priority than non-targeted
            (longer name).
        """
        # Create set of kwargs kw_set for conf steps: {'step_id__kwarg_id'}.
        kw_set = set()
        # Variable for name of *args / **kwarg argument.
        w_name = dict()
        kw_name = dict()
        for ind, step in enumerate(conf['steps']):
            step_id = step[0]
            if step_id in conf['patch']:
                val = conf['patch'][step_id]
                if isinstance(val, str):
                    # if str (ref on existed method).
                    func = getattr(conf['producer'], val)
                else:
                    func = val
            else:
                func = getattr(conf['producer'], step_id)
            w_name[step_id] = '__'
            kw_name[step_id] = '__'
            insp = inspect.signature(func)
            # Check if *args/**kwargs in, find names.
            # [self, 'a', 'b=1', '*args', 'c', 'd=1', '**kwargs'].
            tmp = [str(i) for i in insp.parameters.values()]
            for i in tmp:
                if '**' in i:
                    kw_name[step_id] = i.replace('**', '')
                elif '*' in i:
                    w_name[step_id] = i.replace('*', '')
            expl = step[1]  # dict
            # ('a', 'b', 'args', 'c', 'd', 'kwargs')
            impl = tuple(insp.parameters)
            mrg = set(expl)
            mrg.update(impl)
            kw_set.update({f'{ind}__{step_id}__{i}' for i in mrg})
        # Rearrange global:
        # Sort in level priority.
        key1 = lambda x: x.split('__')[0]  # level
        res = sorted(conf['global'], key=key1)
        # Divide on group
        res2 = itertools.groupby(res, key1)
        # At each level sort on length (could be magic).
        key2 = lambda x: len([i for i in x.split('__') if i])  # len of path
        glob_lis = []
        for i, j in res2:
            glob_lis.extend(sorted(j, key=key2))
        glob_lis = glob_lis[::-1]
        # Find index of 'step_id__kwarg_id' from kw_set among list (-level,
        # -conf,-section).
        # glob_kw_lis contains reduced to step_kwarg/kwarg.
        glob_kw_lis = glob_lis[:]
        self._check_duality(section_id, conf_id, conf, glob_kw_lis)
        #   Substitute value with highest index for each kwarg.
        used_ind = []
        for ind, glob_kw in enumerate(glob_kw_lis):
            if glob_kw is '__':
                continue
            kw_set_ = list(kw_set)  # Dynamically change.
            for kw in kw_set_:
                # could be magic method.
                tmp = kw.split('__')
                step_ind = int(tmp[0])
                kw_id = tmp[-1]
                step_id = ''.join(tmp[1:-1])
                if glob_kw == f"{step_id}__{kw_id}" or glob_kw == kw_id:
                    glob_id = glob_lis[ind]
                    glob = conf['global'][glob_id]
                    if kw_id in [kw_name[step_id], w_name[step_id]]:
                        # Step with **kwargs, *args.
                        # Add possibility to set second level.
                        # Would be problem if any name in both: first & second.
                        conf['steps'][step_ind][1].update(copy.deepcopy(glob))
                    else:
                        conf['steps'][step_ind][1][kw_id] = copy.deepcopy(glob)
                    # Remove to not substitute with lower priority again.
                    kw_set.remove(kw)
                    used_ind.append(ind)
        # Update unused.
        # Remove unused from conf['global']
        tmp = operator.itemgetter(*used_ind)(glob_lis) if used_ind else []
        used = set([tmp]) if len(used_ind) == 1 else set(tmp)
        unused -= used
        for i in list(conf['global'].keys()-used):
            del conf['global'][i]

        return

    def _check_duality(self, section_id, conf_id, conf, glob_kw_lis):
        # If path don`t fit, set '__'(but not check last two).
        # In resolution duality (section vs conf vs step) raise Exception.
        for ind, name in enumerate(glob_kw_lis):
            # Remove level
            level = int(name[6])
            glob_kw_lis[ind] = name[9:]
            # List: ['section_id', 'conf_id', ..]
            # Could be __magic__ paths=step_id.
            zero_magic = False
            tmp = name[9:].split('__')
            if tmp[0] is '':
                zero_magic = True
            paths = [i for i in tmp if i]
            flags = [paths[0] == step[0] if not zero_magic else
                     f"__{paths[0]}__" == step[0] for step in conf['steps']]
            # Length of path, except level.
            lng = len(paths)
            if lng == 0:
                assert False, "zero length"
            if level == 0:
                if lng == 4:
                    if not all([paths[0] == section_id, paths[1] == conf_id]):
                        # Alien.
                        glob_kw_lis[ind] = '__'
                    else:
                        glob_kw_lis[ind] = name[9:]\
                            .replace(f"{section_id}__", '', 1)\
                            .replace(f"{conf_id}__", '', 1)
                elif lng == 3:
                    # 3 variants:
                    # section/cnfg, section/step, cnfg/step
                    if not any([paths[0] == section_id, paths[0] == conf_id]):
                        # Alien.
                        glob_kw_lis[ind] = '__'
                    # Could be better
                    elif any([section_id == conf_id] +
                             [section_id == step[0] or
                              conf_id == step[0] for step in conf['steps']]):
                        raise ValueError(f"Ambiguous global key resolution:\n"
                                         f"    {name}")
                    else:
                        glob_kw_lis[ind] = name[9:]\
                            .replace(f"{section_id}__", '', 1)\
                            .replace(f"{conf_id}__", '', 1)
                elif lng == 2:
                    if not any([paths[0] == section_id, paths[0] == conf_id] +
                               flags):
                        # Alien.
                        glob_kw_lis[ind] = '__'
                    elif (paths[0] == section_id == conf_id or
                          any(flags)
                          and (paths[0] == section_id or paths[0] == conf_id)):
                        raise ValueError(f"Ambiguous global key resolution:\n"
                                         f"    {name}")
                    else:
                        glob_kw_lis[ind] = name[9:]\
                            .replace(f"{section_id}__", '', 1)\
                            .replace(f"{conf_id}__", '', 1)
                elif lng == 1:
                    pass
                else:
                    raise ValueError(f"Too long global kwarg path:\n"
                                     f"   {name}")
            elif level == 1:
                if lng == 3:
                    if not paths[0] == conf_id:
                        # Alien.
                        glob_kw_lis[ind] = '__'
                    else:
                        glob_kw_lis[ind] = name[9:]\
                            .replace(f"{conf_id}__", '', 1)
                elif lng == 2:
                    # 2 variant: conf/kwarg of step/kwarg.
                    if (any(flags)
                            and paths[0] == conf_id):
                        raise ValueError(f"Ambiguous global key resolution:\n"
                                         f"    {name}")
                elif lng == 1:
                    pass
                else:
                    raise ValueError(f"Too long global kwarg path:\n"
                                     f"   {name}")
            elif level == 2:
                if lng > 2:
                    raise ValueError(f"Too long global kwarg path:\n"
                                     f"   {name}")
            else:
                assert False, "level>2"
        return

    def _resolve_none(self, p, section_id, conf_id, ids):
        """Auto resolution for None parameters in endpoint section.

        First search in global, second in sections name.
        """
        # TODO: support for targeted global, currently no need (already set).
        #   Set before substitute to test full workability.
        # TODO: ids support.
        # Keys resolved via global. Exist in global and no separate conf.
        primitive = {key for key in p[section_id][conf_id]['global']
                     if key.replace('_id', '') not in p}
        for key in primitive:
            key_id = key
            # read glob val if exist
            if key_id in p[section_id][conf_id]['global']:
                glob_val = p[section_id][conf_id]['global'][key_id]
            else:
                glob_val = None
            for step in p[section_id][conf_id]['steps']:
                if len(step) <= 1:
                    continue
                step_id = step[0]
                kwargs = step[1]
                if key_id in kwargs:
                    # if None use global
                    if not kwargs[key_id]:
                        kwargs[key_id] = glob_val

        # Keys resolved via separate conf section.
        # Two separate check: contain '_id' or not.
        nonprimitive = {key for key in p.keys()}
        for key in nonprimitive:
            # read glob val if exist
            if key in p[section_id][conf_id]['global']:
                glob_val = p[section_id][conf_id]['global'][key]
            elif f"{key}_id" in p[section_id][conf_id]['global']:
                glob_val = p[section_id][conf_id]['global'][f"{key}_id"]
            else:
                glob_val = None
            if key not in ids:
                ids[key] = set()
            conf = p[section_id][conf_id]
            for step in p[section_id][conf_id]['steps']:
                if len(step) <= 1:
                    continue
                step_id = step[0]
                kwargs = step[1]
                key_id = None
                if key in kwargs:
                    key_id = key
                elif f"{key}_id" in kwargs:
                    key_id = f"{key}_id"
                if key_id:
                    # Step kwargs name(except postfix) match with section name.
                    # Not necessary need to substitute if kwarg name match
                    # section. Substitute only if None or kwarg match with
                    # section__conf (on handler level). Here substitue id,
                    # later in handler val if no id postfix.
                    self._substitute_none(p, section_id, conf_id, ids, key,
                                          glob_val, step_id, kwargs, key_id)
        return None

    def _substitute_none(self, p, section_id, conf_id, ids, key, glob_val,
                         step_id, kwargs, key_id):
        # If None use global.
        if not kwargs[key_id]:
            # If global None use from conf (if only one provided),
            # for metrics not None is guaranteed before.
            if glob_val is None:
                if len(p[key]) > 1:
                    raise ValueError(
                        f"Multiple {key} configurations provided,"
                        f" specify '{key_id}' explicit in:\n"
                        f"    '{section_id}__{conf_id}__{step_id}__{key_id}'"
                        f" or '{section_id}__{conf_id}__global__{key_id}'.")
                else:
                    # Zero position section.
                    glob_val = f"{key}__{list(p[key].keys())[0]}"
            kwargs[key_id] = glob_val

        return None

    def _priority_arrange(self, p):
        """Sort configuration by ``priority`` sub-key."""
        min_heap = []
        for key in p:
            for subkey in p[key]:
                val = p[key][subkey]
                name = f'{key}__{subkey}'
                # [alternative]
                # name = subkey
                priority = val['priority']
                if not isinstance(priority, int) or priority < 0:
                    raise ValueError('Configuration priority should'
                                     ' be non-negative number.')
                if priority:
                    heapq.heappush(min_heap, (priority, (name, val)))
        sorted_ = heapq.nsmallest(len(min_heap), min_heap)
        return list(zip(*sorted_))[1] if len(sorted_) > 0 else []

    def _check_res(self, tup):
        """Check list of tuple for repeated values at first indices."""
        non_uniq = [k for (k, v) in
                    collections.Counter(
                        list(zip(*tup))[0] if len(tup) > 0 else []).items()
                    if v > 1]
        if non_uniq:
            raise ValueError(f"Non-unique configuration id found:\n"
                             f"    {non_uniq}")
        return None

    def _exec(self, oid, conf, objects):
        init = conf['init']
        steps = conf['steps']
        producer = conf['producer']
        patch = conf['patch']
        if inspect.isclass(init):
            init = init()
        elif inspect.isfunction(init):
            init = init()
        if inspect.isclass(producer):
            # Init producer with __init__() decorators.
            ikwargs, idecors = self._init_kwargs(steps)
            producer = functools.reduce(lambda x, y: y(x), idecors,
                                        producer)(objects, oid, **ikwargs)
        else:
            raise TypeError(f"{oid} producer should be a class.")
        producer = self._patch(patch, producer)
        return producer.produce(init, steps)

    def _init_kwargs(self, steps):
        """Extract kwargs to init producer."""
        kwargs = {}
        decors = []
        # Check that first in order or absent.
        for i, step in enumerate(steps):
            if step[0] == '__init__':
                if i != 0:
                    raise IndexError("Method '__init__' should be"
                                     " the first in steps.")

                # Extract and del from list, otherwise produce() will execute.
                # len(step)=3 guaranteed.
                kwargs = steps[0][1]
                decors = steps[0][2]
                # Move out from steps.
                del steps[0]
                break
        return kwargs, decors

    def _patch(self, patch, producer):
        """Monkey-patching producer.

        producer : class object
            Object to patch.
        patch : dict {'method_id' : function/existed 'method_id' }
            Functions to add/rewrite.

        """
        needs_resolve = []
        # Update/add new methods.
        for key, val in patch.items():
            if isinstance(val, str):
                needs_resolve.append((key, val))
                patch[key] = producer.__getattribute__(val)
                continue
            setattr(producer, key, types.MethodType(val, producer))
        # Resolve str name for existed methods.
        for key, name in needs_resolve:
            setattr(producer, key, getattr(producer, name))
        return producer


if __name__ == '__main__':
    pass
