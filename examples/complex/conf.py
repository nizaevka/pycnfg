"""
Example of cross-linked configuration.
There are two sections 'x' and 'y':

* 'x' has multiple configurations 'x__1', 'x__2'.
 'x__1' remains `init` unchanged, 'x__2' patches default `pycnfg.Producer` to
 add 'replace' method and apply it on `init`.
* 'y' has single 'y__conf'.
 'y__conf' uses `CustomProducer` and awaits for 'x__1'/'x__2' object in steps,
  either by value, or by identifier. `CustomProducer`.__init__() awaits for
  'logger_id' and 'path_id'.

Internally ``pycnfg.run``:

* Merging user CNFG with default ``pycnfg.CNFG``, so additional sections
 path and logger will be added.
* Execute available configurations in ``priority`` and add resulted objects to
 `objects` storage:

    * produce 'path__default'.
    * produce 'logger__default'.
    * produce 'x__1', 'x__2'.
    * produce 'y__conf' using previously created objects.

"""


import pycnfg


class CustomProducer(pycnfg.Producer):
    """Specify methods to produce object."""
    def __init__(self, objects, oid, path_id, logger_id):
        pycnfg.Producer.__init__(self, objects, oid)
        self.logger = objects[logger_id]
        self.project_path = objects[path_id]

    def set(self, obj, key, val):
        obj[key] = val
        return obj

    def log(self, obj, key=None, key_id=None):
        if key is None:
            # Extract from cross-configurations storage.
            key = self.objects[key_id]

        self.logger.info(f'{obj[key]}')
        return obj


def func(self, obj, key):
    """Replace obj."""
    obj = key
    return obj


# Configuration.
CNFG = {
    'x': {
        '1': {
            'init': 'a',
            'producer': pycnfg.Producer,
            'steps': [],
        },
        '2': {
            'init': 'b',
            'producer': pycnfg.Producer,
            'patch': {'replace': func},
            'steps': [
                ('replace', {'key': 'c'}),
            ],
        }

    },
    'y': {
        'conf': {
            'init': {'b': 2, 'c': 42},
            'producer': CustomProducer,
            'steps': [
                ('__init__', {'path_id': 'path__default',
                              'logger_id': 'logger__default'}),
                ('set', {'key': 'x__1', 'val': 7}),
                ('log', {'key': 'x__2'}),
                ('log', {'key_id': 'x__2'}),
            ],
        }
    },
}

#  добавь пример на фичи, навроде глобал.

if __name__ == '__main__':
    # Execute configuration(s).
    objects = pycnfg.run(CNFG)
    # => 42
    # => 42

    # Storage for produced object(s).
    print(objects)
    # => {'logger__default': <Logger default (INFO)>,
    #     'path__default': 'pycnfg/examples/complex',
    #     'x__1': 'a',
    #     'x__2': 'c',
    #     'y__conf': {'b': 2, 'c': 42, 'a': 7}}
