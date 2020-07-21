"""The module includes auxiliary utilities."""


import atexit
import importlib
import os
import sys
import warnings

import pycnfg


try:
    from winsound import Beep as Beep
except ImportError:
    def Beep(frequency=400, duration=2000):
        path = '/'.join(__file__.split('/')[:-1])
        os.system(f'aplay {path}/beep.wav')

__all__ = ['find_path', 'run']


def find_path(script_name=False, filepath=None):
    """Get full path to main script.

    Parameters
    ----------
    script_name : bool, optional (default=False)
        If True, return also script name.
    filepath : str, optional (default=None)
        Path to main script. If None and Ipython, get from workdir. If None and
        standard interpreter, get from sys.argv. If sys.argv empty, get from
        working directory.

    Returns
    -------
    project_dir : str
        Full path to start script directory.
    script_name : str, optional if ``script_name`` is True
        Main script name. 'ipython' for Ipython.

    """
    def is_ipython():
        """Return True if ipython else False"""
        try:
            get_ipython = importlib.import_module('IPython', 'get_ipython')
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                # Jupyter notebook or qtconsole.
                return True
            elif shell == 'TerminalInteractiveShell':
                # Terminal running IPython.
                return True
            else:
                # Other type (?).
                return False
        except NameError:
            # Probably standard Python interpreter.
            return False
        except ModuleNotFoundError:
            # No IPython lib installed (check only if Terminal or standard).
            return "idlelib" not in sys.modules
    if filepath is not None:
        temp = filepath.replace('\\', '/').split('/')
        project_dir = '/'.join(temp[:-1])
        script_name_ = temp[-1][:-3]
    elif is_ipython():
        project_dir = os.getcwd().replace('\\', '/')
        script_name_ = 'ipython'
    else:
        # sys.argv provide script_name, but not work in Ipython.
        # For example ['path/run.py', '55'].
        ext_size = 3  # '.py'
        script_name_ = sys.argv[0]\
            .replace('\\', '/')\
            .split('/')[-1][:-ext_size]  # run
        project_dir = sys.argv[0]\
            .replace('\\', '/')[:-len(script_name_)-ext_size]
    if script_name:
        return project_dir, script_name_
    else:
        return project_dir


def run(conf, dcnfg=None, objects=None, beep=False):
    """Wrapper over configuration handler.

    Parameters
    ----------
    conf : dict or str
        Configuration to pass in ``pycnfg.Handler.read()``:
        {'section_id': {'configuration_id': configuration,}}.
        If str, absolute path to the file with ``CNFG`` variable or relative to
        work dir.
    dcnfg : dict, str, optional (default=None)
        Default configurations to pass in ``pycnfg.Handler.read()``.
        If str, absolute path to file with ``CNFG`` variable or relative to
        work dir.
    objects : dict, optional (default=None)
        Dict of initial objects to pass in ``pycnfg.Handler.exec()``:
        {'object_id': object}.
    beep : bool, optional (default=False)
        If True, play sound notification on ending.

    Returns
    -------
    objects : dict
        Dict of objects created by execution all configurations:
        {'section_id__configuration_id': object}.

    See Also
    --------
    :class:`pycnfg.Handler`: Reads configurations, executes steps.

    """
    warnings.simplefilter(action='ignore', category=FutureWarning)
    if beep:
        atexit.register(Beep, 600, 500)
        atexit.register(Beep, 400, 2000)  # Will be the first.

    handler = pycnfg.Handler()
    configs = handler.read(conf, dcnfg=dcnfg)
    objects = handler.exec(configs, objects=objects, debug=True)
    return objects


if __name__ == '__main__':
    pass
