"""Configuration example to produce object."""

import pycnfg


class CustomProducer(pycnfg.Producer):
    """Specify custom methods to produce object."""
    def __init__(self, objects, oid):
        # Mandatory.
        super().__init__(objects, oid)

    def set(self, obj, key, val=42):
        obj[key] = val
        return obj

    def print(self, obj, key='a'):
        print(obj[key])
        return obj

    def method_id(self, obj, *args, **kwargs):
        # Some logic..
        return obj


# Configuration.
#   Set `init` object state {'a': 7}.
#   Set `producer` class CustomProducer.
#   Set `steps` to execute.
CNFG = {
    'section_1': {
        'conf_1': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'steps': [
                ('set', {'key': 'b', 'val': 42}),
                ('print', {}),
                ('print', {'key': 'b'}),
                ('method_id', {}),
            ],
        },
        # 'conf_2': {...}
    }
    # 'section_2': {...}
}

if __name__ == '__main__':
    # Execute configuration(s) in priority.
    objects = pycnfg.run(CNFG)
    # => 7
    # => 42

    # Storage for produced object(s).
    print(objects['section_1__conf_1'])
    # => {'a': 7, 'b': 42}
