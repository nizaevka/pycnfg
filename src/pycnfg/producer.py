"""
The :mod:`pycnfg.produce` includes class to produce configuration object.
Use it as Mixin to add desired endpoints.

Support method to cache/read intermediate state of object (pickle/unpickle).
It useful to save time when reusing a configuration. Also python dictionary api
forwarding is supported.

"""


import functools
import glob
import importlib
import logging
import os
import sys

import pycnfg


class Producer(object):
    """Execute configuration steps.

    Interface: produce, dump_cache, load_cache, dict_api.

    Parameters
    ----------
    objects : dict
        Dictionary with resulted objects from previous executed producers:
        {'section_id__config__id', object}.
    oid : str
        Unique identifier of produced object.
    path_id: str, optional (default='path_default')
        Unique identifier of project path in ``objects``. If not exist, raise
        error if used by producer.
    logger_id: str, optional (default='logger_default')
        Unique identifier of logger either in ``objects`` or
        :data:`logging.root.manager.loggerDict` . If not found, attach
        new logger to stdout (with logger_id name and 'info' level).

    Attributes
    ----------
    objects : dict
        Dictionary with resulted objects from previous executed producers:
        {'section_id__config__id', object,}
    oid : str
        Unique identifier of produced object.
    logger : logger object
        Logger.
    project_path: None
        Absolute path to project dir.

    """
    _required_parameters = ['objects', 'oid']

    def __init__(self, objects, oid, path_id='path__default',
                 logger_id='logger__default'):
        if logger_id in objects:
            logger = objects[logger_id]
        elif logger_id in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_id)
        else:
            # Temporary, garbage collected (in opposite to getLogger())
            logger = logging.Logger(logger_id)
            logger.addHandler(logging.StreamHandler(stream=sys.stdout))
            logger.setLevel("INFO")

        if path_id in objects:
            project_path = objects[path_id]
        else:
            # Should be set either in objects or as configuration.
            # Otherwise double execution for path config.
            project_path = None

        self.objects = objects
        self.oid = oid
        self.logger = logger
        self.project_path = project_path

    def produce(self, init, steps):
        """Execute configuration steps.

        Consecutive call (with decorators):

        ``init = getattr(self, 'method_id')(init, objects=objects, **kwargs)``

        Parameters
        ----------
        init: object
            Will be passed as arg in each step and get back as result.
        steps : list of tuples
            List of ``self`` methods to run consecutive with kwargs:
            ('method_id', kwargs, decorators ).

        Returns
        -------
        configs : list of tuple
            List of configurations, prepared for execution:
            [('section_id__config__id', config), ...].

        Notes
        -----
        Object identifier ``oid`` auto added, if produced object has ``oid``
        attribute.

        """
        self.logger.info(f"|__ CONFIGURATION: {self.oid}")
        self.logger.debug(f"steps:\n"
                          f"    {[i[0] for i in steps]}")
        res = init
        for step in steps:
            self.logger.debug(f"step:\n"
                              f"    {step[0]}")
            # len(step)=3 guaranteed.
            method = step[0]
            kwargs = step[1]
            decors = step[2]
            self.logger.info(f"    |__ {method.upper()}")
            if not isinstance(kwargs, dict):
                raise ValueError(f"Kwargs for step '{method}' "
                                 f"should be a dictionary.")
            kwargs = self._resolve_object(kwargs, self.objects)
            res = functools.reduce(lambda x, y: y(x), decors,
                                   getattr(self, method))(res, **kwargs)
        # Add identifier if provided.
        # Avoid hasattr(res, 'oid') to prevent execution.
        if 'oid' in dir(res):
            res.oid = self.oid
        res = self._check(res)
        return res

    def dump_cache(self, obj, prefix=None, cachedir=None, pkg='pickle',
                   **kwargs):
        """Dump intermediate object state to IO.

        Parameters
        ----------
        obj : picklable
            Object to dump.
        prefix : str, optional (default=None)
            File identifier, added to filename. If None, 'self.oid' is used.
        cachedir : str, optional(default=None)
            Absolute path to dump dir or relative to 'project_path' started
            with './'. Created, if not exists. If None, "sproject_path/
            .temp/objects" is used.
        pkg : str, optional (default='pickle')
            Import package and try ``pkg``.dump(obj, file, **kwargs).
        **kwargs : kwargs
            Additional parameters to pass in .dump().

        Returns
        -------
        obj : picklable
            Unchanged input for compliance with producer logic.

        """
        if prefix is None:
            prefix = self.oid
        if cachedir is None:
            cachedir = f"{self.project_path}/.temp/objects"
        elif cachedir.startswith('./'):
            cachedir = f"{self.project_path}/{cachedir[2:]}"

        # Create .temp dir for cache if not exist.
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
        for filename in glob.glob(f"{cachedir}/{prefix}*"):
            os.remove(filename)
        fps = set()

        # pickle, dill, joblib.
        pkg_ = importlib.import_module(pkg)
        filepath = f'{cachedir}/{prefix}_.dump'
        with open(filepath, mode='wb') as f:
            pkg_.dump(obj, f, **kwargs)

        fps.add(filepath)
        self.logger.warning('Warning: update cache file(s):\n'
                            '    {}'.format('\n    '.join(fps)))
        return obj

    def load_cache(self, obj, prefix=None, cachedir=None, pkg='pickle',
                   **kwargs):
        """Load intermediate object state from IO.

        Parameters
        ----------
        obj : picklable
            Object template, for producer logic only (ignored).
        prefix : str, optional (default=None)
            File identifier. If None, 'self.oid' is used.
        pkg : str, optional default('pickle')
            Import package and try obj = ``pkg``.load(file, **kwargs).
        cachedir : str, optional(default=None)
            Absolute path to load dir or relative to 'project_path' started
            with './'. If None, 'project_path/.temp/objects' is used.
        **kwargs : kwargs
            Additional parameters to pass in .load().

        Returns
        -------
        obj : picklable object
            Loaded cache.

        """
        if prefix is None:
            prefix = self.oid
        if cachedir is None:
            cachedir = f"{self.project_path}/.temp/objects"
        elif cachedir.startswith('./'):
            cachedir = f"{self.project_path}/{cachedir[2:]}"

        pkg_ = importlib.import_module(pkg)
        filepath = f'{cachedir}/{prefix}_.dump'
        with open(filepath, mode='rb') as f:
            obj = pkg_.load(f, **kwargs)

        self.logger.warning(f"Warning: use cache file(s):\n    {cachedir}")
        return obj

    def dict_api(self, obj, method='update', **kwargs):
        """Forwarding api for dictionary object.

        Could be useful to add/pop keys via configuration steps. For example
        to proceed update: ('dict_api', {'b':7} )
        """
        if not isinstance(obj, dict):
            raise TypeError('Object should be a dictionary.')

        _ = getattr(obj, method)(**kwargs)

        return obj

    def update(self, obj, items):
        """Update key(s) for dictionary object.

        Parameters
        ----------
        obj : dict
            Object to update.
        items : dict, list, optional (default=None)
            Either dictionary or items [(key,val),] to update ``obj``.

        Returns
        -------
        obj : dict
            Updated input.

        """
        if not isinstance(obj, dict):
            raise TypeError('Object should be a dictionary.')

        obj.update(items)
        return obj


    def _resolve_object(self, kwargs, objects):
        """Substitute objects in kwargs.

        If val not ends with '_id'. For str val (or str subval in list val)
        looks up in ``objects`` the key__val, replace if found.
        """
        for key, val in kwargs.items():
            if not key.endswith('_id'):
                # For compliance with list.
                val_ = val if isinstance(val, list) else [val]
                resolved = [objects[v] if isinstance(v, str) and v in objects
                            else v for v in val_]
                kwargs[key] = resolved if isinstance(val, list)\
                    else resolved[0]

        return kwargs

    def _check(self, res):
        """Additional result check."""
        return res


if __name__ == '__main__':
    pass
