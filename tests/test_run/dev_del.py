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


def kw_func(self, obj, key,  **kwargs):
    obj[key] = kwargs['val']
    return obj


CNFG = {
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
        }

objects = pycnfg.run(CNFG, dcnfg={}, objects=None)  # 'test_run/example_conf.py'
print(str(objects))
