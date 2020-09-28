"""
Example of configuration syntax.
There are multiple CNFG provided equivalent result:

* set key 'b' with 42.
* log.

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


# Original.
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

# Use CNFG level 'global' to rewrite 'key' from 'c' to 'b' in 'set'/'print'.
# Use section level 'global' to rewrite 'val' from '24' on '42'.
# NOTE: In pycnfg.run() should be set update_expl=True to allow replace
# explicitly set kwargs with global values (by default False).
CNFG_2 = {
    'global': {
        'key': 'b',
        'print__key': 'b',  # Targeted alternative (higher priority).
    },
    'init': {'a': 7},
    'section_id': {
        'global': {'val': 42},
        'configuration_id': {
            'producer': CustomProducer,
            'steps': [
                ('set', {'key': 'c', 'val': 24}),
                ('print', {'key': 'c'}),
            ],
        }
    }
}

# Resolve None via separate sections.
# Sections could be reused multiple times.
# NOTE: In pycnfg.run() should be set resolve_none=True to allow resolve
# explicitly set to None kwargs via sub-configuration (by default False).
CNFG_3 = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'priority': 2,
            'steps': [
                ('set', {'key': None, 'val': None}),
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

# Resolve values via separate section id.
CNFG_4 = {
    'section_id': {
        'configuration_id': {
            'init': {'a': 7},
            'producer': CustomProducer,
            'priority': 2,
            'steps': [
                ('set', {'key': 'key__conf', 'val': 'val__conf2'}),
                ('print', {'key': 'key__conf'}),
            ],
        }
    },
    'key': {
        'conf': {
            'init': 'b',
        },
    },
    'val': {
        'conf': {
            'init': 24,
        },
        'conf2': {
            'init': '42',
        }
    },

}

if __name__ == '__main__':
    for cnfg in [CNFG_1, CNFG_2, CNFG_3, CNFG_4]:
        # Execute configuration(s).
        objects = pycnfg.run(cnfg, dcnfg={}, update_expl=True, resolve_none=True)
        # => 42

        # Storage for produced object(s).
        print(objects['section_id__configuration_id'])
        # => {'a': 7, 'b': 42}
        print('=' * 79)
