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
                'section_id__conf_id__step_id__val': 1,
                'section_id__step_id__val': 2,
                'section_id__conf_id__val': 3,
                'section_id__val': 4,
                'conf_id__step_id__val': 5,
                'conf_id__val': 6,
                'step_id__val': 7,
                'val': 8,
            },
            'section_id': {
                'global': {
                    'conf_id__step_id__val': 9,
                    'conf_id__val': 10,
                    'step_id__val': 11,
                    'val': 12,
                },
                'conf_id': {
                    'global': {
                        'step_id__val': 13,
                        'val': 14,
                    },
                    'init': {'a': 7},
                    'producer': CustomProducer,
                    'patch': {'step_id': 'set'},
                    'steps': [
                        ('set', {'key': 'b', 'val': 24},),
                    ],
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
