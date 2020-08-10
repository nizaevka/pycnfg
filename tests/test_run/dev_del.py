import pycnfg


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


CNFG = {
            'global': {
                'section_id__conf_id__set__key': 'a',
                'section_id__conf_id__key': 'a',
                'conf_id__key': 'a',
                'val': 43,
            },
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
            'section2_id': {
                'global': {
                    'conf2_id__set__key': 'c',
                    'conf2_id__key': 'c',
                    'val': '44',
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
            }
        }


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

dcnfg = {
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
        }

objects = pycnfg.run(CNFG, dcnfg={}, objects=None)  #'test_run/example_conf.py'
print(str(objects))
