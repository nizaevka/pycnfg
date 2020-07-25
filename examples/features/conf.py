"""
Example of configuration syntax.
There are three CNFG provided equivalent result: set key 'b' with 42 and print.

"""

import pycnfg


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


# Explicit.
CNFG_1 = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'steps': [
                ('set', {'key': 'b', 'val': 42}),
                ('print', {'key': 'b'}),
            ],
        }
    }
}

# Resolve None via 'global', 'val' 42 auto moved to 'global').
CNFG_2 = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'val': 42,
            'global': {'key': 'b'},
            'steps': [
                ('set', {'key': None, 'val': None}),
                ('print', {'key': None}),
            ],
        }
    }
}

# Resolve None via separate sections.
# Sections could be reused multiple times.
CNFG_3 = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'priority': 2,
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

}


if __name__ == '__main__':
    for cnfg in [CNFG_1, CNFG_2, CNFG_3]:
        # Execute configuration(s).
        objects = pycnfg.run(cnfg, dcnfg={})
        # => 42

        # Storage for produced object(s).
        print(objects['section_id__configuration_id'])
        # => {'a': 7, 'b': 42}
