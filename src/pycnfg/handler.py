"""
The :class:`pycnfg.Handler` contains class to read and execute configuration(s).

The purpose of any configuration is to produced result (object) by combining
resources (steps). Pycnfg offers unified patten to create arbitrary Python
objects pipeline-wise. That naturally allows to control all parameters via
single configuration.

Configuration is a python dictionary. It supports multiple sections. Each
section specify set of sub-configurations. Each sub-configuration provide steps
to construct an object, that can be utilize as argument in other sections.
Whole configuration could be passed to ``pycnfg.run`` or to user-defined
wrapper around ``pycnfg.Handler``, that builds underlying sub-configuration``s
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

* takes ``init`` and consecutive pass it and kwargs to ``steps`` methods.

* returns resulting object.

 That can be used as kwargs for any step in others sections. To specify the
 order in which sections handled, the 'priority' key is available in each
 sub-configuration.

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

        If `value` is set to None, parser try to resolve it. First searches for
        value in ``global``. Then resolver looks up 'kwarg' in section names.
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

global : dict {'kwarg_name': value, ...}, optional (default={})
    Specify values to resolve None for arbitrary kwargs. This is convenient for
    example when we use the same kwarg in all methods. It is doesn't rewrite
    not-None values.

**keys : dict {'kwarg_name': value, ...}, optional (default={})
    All additional keys in configuration are moving to ``global`` automatically
    that rewrites already existed (useful if mostly rely on default).

Notes
-----
To add functionality to producer use ``patch`` key or inheritance from
:class:pycnfg.Producer.

Default configurations can be set in ``pycnfg.Handler.read(cnfg,
dcnfg=default)``.
``section_id``/``configuration_id`` should not contain double underscore '__'.

Examples
--------
Patching producer with custom function.

.. code-block::

    def my_func(self, *args, **kwargs):
        # ... custom logic ...
        return res

    CNFG = {..{'patch': {'extra': my_func,},}

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

    def read(self, cnfg, dcnfg=None):
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
            If None, read from ``pycnfg.CNFG``.

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
         not exist at all, use default values for sub-keys: {'init': {},
         'priority': 1, 'class': pycnfg.Producer, 'global': {}, 'patch': {},
         'steps': [],}.

        Resolve kwargs:

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
        configs = self._parse_cnfg(cnfg, dcnfg)
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
                print(config)
            oid, val = config
            objects[oid] = self._exec(oid, val, objects)
        return objects

    def _parse_cnfg(self, p, dp):
        # Apply default.
        p = self._merge_default(p, dp)
        # Resolve None inplace for configurations.
        # ``ids`` contain used confs ref by section.
        ids = {}  # {'section_id': set('configuration_id', )}
        for section_id in p:
            for conf_id in p[section_id]:
                self._resolve_none(p, section_id, conf_id, ids)

        # [deprecated] add -1 priority to skip conf.
        # in common config we need all objects
        # and explicit kwargs list not available.
        # # Remain only used configuration.
        # res = {}
        # for key, val in ids.items():
        #     if val:
        #         res[key] = {id_: p[key][id_] for id_ in val}
        # p = res

        # Arrange in priority.
        res = self._priority_arrange(p)  # [('section_id__config__id', config)]
        self._check_res(res)
        return res

    def _merge_default(self, p, dp):
        """Add skipped key from default.

        * Copy skipped sections from dp (could be multiple confs).
        * Copy skipped sub-keys from dp section(s) of the same name.
         If dp section contains multiple confs, search for match, otherwise use
         zero position conf.
        * Fill skipped sub-keys for section not existed in dp.
         {'init': {}, 'class': pycnfg.Producer, 'global': {}, 'patch': {},
         'priority': 1, 'steps': [],}
         * Fill skipped steps {kwargs:{}, decorators:[]}

        """
        for section_id in dp:
            if section_id not in p:
                # Copy skipped section_ids from dp.
                p[section_id] = copy.deepcopy(dp[section_id])
            else:
                # Copy skipped sub-keys for existed in dp conf(zero position).
                dp_conf_ids = list(dp[section_id].keys())
                for conf_id, conf in p[section_id].items():
                    if conf_id in dp[section_id]:
                        dp_conf_id = conf_id
                    else:
                        # Get zero position dp conf in section.
                        dp_conf_id = dp_conf_ids[0]
                    for subkey in dp[section_id][dp_conf_id].keys():
                        if subkey not in conf:
                            conf[subkey] = copy.deepcopy(
                                dp[section_id][dp_conf_id][subkey])

        dkeys = {
            'init': {},
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        }
        for section_id in p:
            # Add dkeys.
            if section_id not in dp:
                for conf_id, conf in p[section_id].items():
                    miss_subkeys = set(dkeys)-set(conf)
                    conf.update({key: dkeys[key] for key in miss_subkeys})
            # Add empty kwargs/decorator to 'steps' (including __init__).
            for conf_id, conf in p[section_id].items():
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

    def _resolve_none(self, p, section_id, conf_id, ids):
        """Auto resolution for None parameters in endpoint section."""
        # [alternative] update with global when call step.

        # Assemble unknown keys to global.
        for key in list(p[section_id][conf_id].keys()):
            if key not in ['init', 'producer', 'global',
                           'patch', 'steps', 'priority']:
                p[section_id][conf_id]['global']\
                    .update({key: p[section_id][conf_id].pop(key)})

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
        # two separate check: contain '_id' or not.
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
                    # section. Substitute only if None or val match with
                    # section__conf (on handler level).
                    self._substitute(p, section_id, conf_id, ids,
                                     key, glob_val, step_id, kwargs, key_id)
        return None

    def _substitute(self, p, section_id, conf_id, ids,
                    key, glob_val, step_id, kwargs, key_id):
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
                    glob_val = f"{key}__{list(p[key].keys())[0]}"
            kwargs[key_id] = glob_val

        return None

    def _priority_arrange(self, res):
        """Sort configuration by ``priority`` sub-key."""
        min_heap = []
        for key in res:
            for subkey in res[key]:
                val = res[key][subkey]
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
            # Init producer with decorators.
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
        # update/add new methods
        for key, val in patch.items():
            if isinstance(val, str):
                needs_resolve.append((key, val))
                patch[key] = producer.__getattribute__(val)
            setattr(producer, key, types.MethodType(val, producer))
        # resolve str name for existed methods
        for key, name in needs_resolve:
            setattr(producer, key, getattr(producer, name))
        return producer


if __name__ == '__main__':
    pass
