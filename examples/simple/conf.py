"""
Example of configuration to produce object.
"""

import pycnfg


class Producer(pycnfg.Producer):
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

    def method_id(self, obj, *args, **kwargs):
        # Some logic..
        return obj


# Configuration.
#   Set `init` object state.
#   Set `producer` class.
#   Set `steps` to execute.
CNFG = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': Producer,
            'steps': [
                ('set', {'key': 'b', 'val': 24}),
                ('print', {}),
                ('print', {'key': 'b'}),
                ('method_id', {}),
            ],
        }
    }
}

if __name__ == '__main__':
    # Execute configuration(s).
    objects = pycnfg.run(CNFG, dcnfg={})
    # => 7
    # => 42

    # Storage for produced object(s).
    print(objects['section_id__configuration_id'])
    # => {'a': 7, 'b': 42}
