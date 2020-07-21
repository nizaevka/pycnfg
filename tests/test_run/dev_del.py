import pycnfg

CNFG = {
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
                    # Needs for list of id/val
                    'init': 'cross-section2',
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

objects = pycnfg.run(CNFG, dcnfg=dcnfg, objects=None)  #'test_run/example_conf.py'
print(str(objects))
