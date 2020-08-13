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
    def __init__(self, objects, oid, param=None):
        # Mandatory.
        super().__init__(objects, oid)
        self.param = param

    def set(self, obj, key, val=42):
        obj[key] = val
        return obj

    def print(self, obj, key='a'):
        print(obj[key])
        return obj


def decorator(func):
    def wrapper(*args, **kwargs):
        print('Apply decorator.')
        result = func(*args, **kwargs)
        return result
    return wrapper


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


def kw_func(self, obj, key,  **kwargs):
    obj[key] = kwargs['val']
    return obj


params = [
    # Args combinations.
    (
        0,
        [{}],
        {},
        out,
    ),
    (
        1,
        [{}],
        {'resolve_none': True},
        out,
     ),
    (
        2,
        [{}],
        {'dcnfg': {}},
        {},
    ),
    (
        3,
        [{}],
        {'dcnfg': {}, 'objects': {'a__b': 7}, 'debug': True, 'beep': True},
        {'a__b': 7},
    ),
    (
        4,
        [f'{currdir}/example_conf.py'],
        {'dcnfg': {}},
        out
    ),
    (
        5,
        [{}],
        {'dcnfg': f'{currdir}/example_conf.py'},
        out,
    ),
    (
        6,
        [f'{currdir}/example_conf.py'],
        {'dcnfg': f'{currdir}/example_conf.py'},
        out,
    ),
    # Different conf with empty default.
    # Skip all sub-keys.
    (
        7,
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
        8,
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
        {'dcnfg': {}, 'resolve_none': True},
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
        9,
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
        10,
        [f'{currdir}/complex_conf.py'],
        {'resolve_none': True},
        {**out, 'x__2': 'c', 'y__conf': {'b': 2, 'c': 42, 'print': 252}}
    ),
    # [v] Separate primitive section.
    # [v] Empty init and not-init.
    (
        11,
        [{
            'section_id': {
                'configuration_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('__init__',),
                        ('set', {'key': None, 'val': 42}),
                        ('print', {'key': None}),
                        ('print', ),
                    ],
                    'priority': 2,
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
        {'dcnfg': {}, 'resolve_none': True},
        {'key__conf': 'b',
         'section_id__configuration_id': {'a': 7, 'b': 42},
         'val__conf': 42}
    ),
    # [v] decorators (multiple init and non-init)
    (
        12,
        [{
            'section_id': {
                'configuration_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('__init__', {}, [decorator, decorator]),
                        ('set', {'key': 'b', 'val': 42}, [decorator,
                                                          decorator]),
                        ('print', {'key': 'a'}),
                    ],
                    'priority': 1,
                }
            },
        }],
        {'dcnfg': {}},
        {'section_id__configuration_id': {'a': 7, 'b': 42}}
    ),
    # [v] configuration/section global (special and usual).
    (
        13,
        [{
            'global': {
                'section_id__conf_id__set__key': 'a',
                'section_id__conf_id__key': 'e',
                'conf_id__key': 'd',
                'val': 43,
            },
            'section_id': {
                'global': {
                    'conf_id__print__key': 'a',
                },
                'conf_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('set', {'key': 'b', 'val': 42},),
                        ('print', {'key': 'a'}),
                    ],
                    'priority': 1,
                }
            },
            'section2_id': {
                'global': {
                    'conf2_id__set__key': 'c',
                    'conf2_id__key': 'c',
                    'val': 44,
                },
                'conf2_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('set', {'key': 'b', 'val': 42},),
                        ('print', {'key': 'a'}),
                    ],
                    'priority': 1,
                },
                'conf_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('set', {'key': 'b', 'val': 42},),
                        ('print', {'key': 'a'}),
                    ],
                    'priority': 1,
                },
            },

        }],
        {'dcnfg': {}},
        {
            'section_id__conf_id': {'a': 43},
            'section2_id__conf2_id': {'a': 7, 'c': 44},
            'section2_id__conf_id': {'a': 7, 'd': 44},
        }
    ),
    # [v] transfer dcnfg global.
    (
        14,
        [{
            'section_id': {
                'conf_id': {
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'steps': [
                        ('set', {'key': 'b', 'val': 42},),
                        ('print', {'key': 'a'}),
                    ],
                    'priority': 1,
                }
            },

        }],
        {'dcnfg': {
            'global': {
                'conf_id__key': 'a',
                'val': 43,
            },
            'section_id': {
                'global': {
                    'conf_id__set__key': 'c',
                    'val': 44,
                },
                'conf_id': {
                }
            },
        }},
        {
            'section_id__conf_id': {'a': 7, 'c': 44},
        }
    ),
    # [v] set via global second level kwargs.
    (
        15,
        [{
            'section_id': {
                'conf_id': {
                    'init': {},
                    'patch': {'set': kw_func},
                    'global': {'kwargs': {'val': 42}},
                    'steps': [
                        ('set', {'key': 'b'},),
                    ],
                    'priority': 1,
                },
                'conf2_id': {
                    'init': {},
                    'patch': {'set': kw_func},
                    'global': {'val': 42},
                    'steps': [
                        ('set', {'key': 'b', 'val': 24},),
                    ],
                    'priority': 1,
                }
            },
        }],
        {'dcnfg': {}},
        {
            'section_id__conf_id': {'b': 42},
            'section_id__conf2_id': {'b': 42},
        }
    ),
    # [v] set global (init, producer..).
    (
        16,
        [{
            'global': {
                'section_1__conf_1__set__val': 42,
                'val': 99,
                },
            'steps': [
                ('set', {'key': 'c', 'val': 24},),
            ],
            'producer': CustomProducer,

            'section_1': {
                'init': {'a': 7},
                'conf_1': {
                    'steps': [
                        ('set', {'key': 'b', 'val': 24},),
                    ],
                },
                'conf_2': {
                },
            }
        }],
        {'dcnfg': {}},
        {
            'section_1__conf_1': {'a': 7, 'b': 42},
            'section_1__conf_2': {'a': 7, 'c': 99},
        }
    ),
]
