"""
The :mod:`pycnfg.produce` includes class to produce configuration object.
Use it as Mixin to add desired endpoints.

Support method to cache/read intermediate state of object (pickle/unpickle).
It useful to save time when reusing a configuration.

"""


import glob
import importlib
import logging
import os
import sys

import pycnfg


class Producer(object):
    """Execute configuration steps.

    Interface: produce, dump_cache, load_cache.

    Parameters
    ----------
    objects : dict
        Dictionary with resulted objects from previous executed producers:
        {'section_id__config__id', object}.
    oid : str
        Unique identifier of produced object.

    Attributes
    ----------
    objects : dict
        Dictionary with resulted objects from previous executed producers:
        {'section_id__config__id', object,}
    oid : str
        Unique identifier of produced object.
    logger : logger object
        Default logger logging.getLogger().
    project_path: None
        Absolute path to project dir pycnfg.find_path().

    """
    _required_parameters = ['objects', 'oid']

    def __init__(self, objects, oid):
        logger = logging.getLogger(oid)
        logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        logger.setLevel("INFO")

        self.objects = objects
        self.logger = logger
        self.project_path = pycnfg.find_path()
        self.oid = oid

    def produce(self, init, steps):
        """Execute configuration steps.

        consecutive:
        init = getattr(self, 'method_id')(init, objects=objects, **kwargs)`

        Parameters
        ----------
        init: object
            Will be passed as arg in each step and get back as result.
        steps : list of tuples ('method_id', {**kwargs})
            List of `self` methods to run consecutive with kwargs.

        Returns
        -------
        configs : list of tuple [('section_id__config__id', config), ...]
            List of configurations, prepared for execution.

        Notes
        -----
        Object identifier `oid` added, if produced object has `oid` attribute.

        """
        self.logger.info(f"|__ CONFIGURATION: {self.oid}")
        self.logger.debug(f"steps:\n"
                          f"    {steps}")
        res = init
        for step in steps:
            self.logger.debug(step)
            method = step[0]
            kwargs = step[1] if len(step) > 1 else {}
            if not isinstance(kwargs, dict):
                raise ValueError(f"Kwargs for step '{method}' "
                                 f"should be a dictionary.")
            kwargs = self._resolve_object(kwargs, self.objects)
            res = getattr(self, method)(res, **kwargs)
        # Add identifier.
        if hasattr(res, 'oid'):
            res.oid = self.oid
        res = self._check(res)
        return res

    def dump_cache(self, obj, prefix=None, cachedir=None, pkg='pickle',
                   **kwargs):
        """Pickle intermediate object state to disk.

        Parameters
        ----------
        obj : picklable
            Object to dump.
        prefix : str, optional (default=None)
            File identifier, added to filename. If None, 'self.oid' is used.
        cachedir : str, optional(default=None)
            Absolute path dump dir or relative to 'self.project_dir' started
            with './'. Created, if not exists. If None,"self.project_path/.temp
            /objects" is used.
        pkg : str, optional default('pickle')
            Import package and try `pkg`.dump(obj, file, **kwargs).
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
        """Load intermediate object state from disk.

        Parameters
        ----------
        obj : picklable
            Object template, for producer logic only (ignored).
        prefix : str, optional (default=None)
            File identifier. If None, 'self.oid' is used.
        pkg : str, optional default('pickle')
            Import package and try obj = `pkg`.load(file, **kwargs).
        cachedir : str, optional(default=None)
            Absolute path load dir or relative to 'self.project_dir' started
            with './'. If None, 'self.project_path/.temp/objects' is used.
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

    def _resolve_object(self, kwargs, objects):
        """Substitute objects in kwargs.


        If val not ends with '_id'. For val that str (or str in list) looks up \
        in `objects` key__val, replace if found.
        """
        for key, val in kwargs.items():
            if not key.endswith('_id'):
                if not isinstance(val, list):
                    # For compliance with list.
                    val = [val]
                resolved = [objects[v] if isinstance(v, str) and v in objects
                            else v for v in val]
                kwargs[key] = resolved if len(val) > 1 else resolved[0]

        return kwargs

    def _check(self, res):
        """Additional result check."""
        return res


if __name__ == '__main__':
    pass
