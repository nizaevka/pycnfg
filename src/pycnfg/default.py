"""The module contains default configuration."""

import logging
import sys

import pycnfg

__all__ = ['CNFG']

logger = logging.getLogger('default')
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel('INFO')

CNFG = {
    'path': {
        'default': {
            'init': pycnfg.find_path,
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        },
    },
    'logger': {
        'default': {
            'init': logger,
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        },
    },

}
"""dict: Default configuration.

Specifies logger and project_path objects.
"""


if __name__ == '__main__':
    pass
