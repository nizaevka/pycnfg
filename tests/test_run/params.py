"""
Params to test `pycnfg.run`. [(args, kwargs, result), ..].
Only for import (relate on workdir).
"""
import logging
import pathlib
import sys

import pycnfg

currdir = pathlib.Path(__file__).parent.absolute()
workdir = pathlib.Path().absolute()

# Typical output.
logger = logging.getLogger('default')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(1)
out = {'logger__default': logger, 'path__default': str(workdir)}


class CustomProducer(pycnfg.Producer):
    """Specify methods to produce object."""
    def __init__(self, objects, oid):
        # Mandatory.
        super().__init__(objects, oid)

    def set(self, obj, key, val=42):
        obj[key] = val
        return obj

    def print(self, obj, key='a'):
        print(obj[key])
        return obj


# patch
def func_1(self, res, param):
    res['param'] = param
    return res


def func_2(self, res, param_id):
    res['param_id'] = param_id
    return res


def func_3(self, res, params):
    res['params'] = params
    return res


def func_4(self, res, params_id):
    res['params_id'] = params_id
    return res


def new_dump_cache(self, res, **kwargs):
    res['replace_dump'] = True
    return res


params = [
    # Args combinations.
    (
        [{}],
        {},
        out,
     ),
    (
        [{}],
        {'dcnfg': {}},
        {},
    ),
    (
        [{}],
        {'dcnfg': {}, 'objects': {'a__b': 7}},
        {'a__b': 7},
    ),
    (
        [f'{currdir}/example_conf.py'],
        {'dcnfg': {}},
        out
    ),
    (
        [{}],
        {'dcnfg': f'{currdir}/example_conf.py'},
        out,
    ),
    (
        [f'{currdir}/example_conf.py'],
        {'dcnfg': f'{currdir}/example_conf.py'},
        out,
    ),
    # Different conf with empty default.
    # Skip all sub-keys.
    (
        [{'section': {
            'config': {},
        }, }],
        {'dcnfg': {}},
        {'section__config': {}},
    ),
    # [v] resolving None
    #    via global, via section, remain None
    # [v] global, unknown keys.
    # [v] dump_cache, load_cache
    (
        [{
            'section1': {
                'config1': {
                    'prefix': 'del',
                    'init': {},
                    'producer': pycnfg.Producer,
                    'global': {},
                    'patch': {},
                    'priority': 2,
                    'steps': [('dump_cache', {'prefix': None, 'pkg': None,
                                              'cachedir': None}),
                              ('load_cache', {'prefix': None, 'pkg': None,
                                              'cachedir': None})],
                },
            },
            'pkg': {
                'config': {
                    'init': 'pickle',
                    'priority': 1,
                },
            },
        }],
        {'dcnfg': {}},
        {'section1__config1': {}, 'pkg__config': 'pickle'},
    ),
    # V init: callable or instance.
    # V patch: new, existed.
    # V priority 0,1,2.
    # V separate section for arbitrary kwarg.
    #   pass section__config by val/ by id/ by list of id/ bylist of val.
    # V Match section__config name with default or not.
    # V cross-interaction between section.
    # V steps order.
    (
        [{
            'section1': {
                'config1': {
                    'init': {},
                    'producer': pycnfg.Producer,
                    'global': {},
                    # Others should get from default section1__config1 (match).
                },
                'config2': {
                    'init': dict,
                    'producer': pycnfg.Producer,
                    'global': {},
                    'priority': 2,
                    # Others should get from default section1__config3 (zero).
                },
                'config4': {
                    'priority': 0,
                }
            },
            'section2': {
                'config2': {
                     'init': 'cross-section',
                     'producer': pycnfg.Producer,
                     'global': {},
                     'patch': {},
                     'priority': 1,
                     'steps': [],
                },
                'config3': {
                    # Needs for list of id/val.
                    'init': 'cross-section2',
                },
            },
        }],
        {'dcnfg': {
            'section1': {
                'config3': {
                    'init': {},
                    'producer': pycnfg.Producer,
                    'global': {},
                    'priority': 1,
                    'patch': {'func_1': func_1,
                              'func_2': func_2,
                              'func_3': func_3,
                              'func_4': func_4,
                              },
                    'steps': [('func_1', {'param': 1}),
                              ('func_1', {'param': 'section2__config2'}),
                              ('func_2', {'param_id': 'section2__config2'}),
                              ('func_3', {'params': ['section2__config2',
                                                     'section2__config3']}),
                              ('func_4', {'params_id': ['section2__config2',
                                                        'section2__config3']}),

                              ],
                },
                'config1': {
                    'init': {},
                    'producer': pycnfg.Producer,
                    'global': {},
                    'patch': {'dump_cache': new_dump_cache},
                    'priority': 1,
                    'steps': [('dump_cache', {})],
                },
            },
        }},
        {
            'section1__config1': {'replace_dump': True},
            'section2__config2': 'cross-section',
            'section2__config3': 'cross-section2',
            'section1__config2': {
                'param': 'cross-section',
                'param_id': 'section2__config2',
                'params': ['cross-section', 'cross-section2'],
                'params_id': ['section2__config2', 'section2__config3'],
            }
         },
    ),
    # [v] Resolver global/section (by val/by id).
    # [v] CustomProducer.
    # [v] __init__
    (
        [f'{currdir}/complex_conf.py'],
        {},
        {**out, 'x__2': 'c', 'y__conf': {'b': 2, 'c': 42, 'print': 252}}
    ),
    # [v] Separate primitive section.
    (
        [{
            'section_id': {
                'configuration_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('set', {'key': None, 'val': 42}),
                        ('print', {'key': None}),
                    ],
                }
            },
            'key': {
                'conf': {
                    'init': 'b',
                }
            },
            'val': {
                'conf': {
                    'init': 42,
                }
            },

        }],
        {'dcnfg': {}},
        {'key__conf': 'b',
         'section_id__configuration_id': {'a': 7, 'b': 42},
         'val__conf': 42}
    ),
]
