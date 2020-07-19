"""Conf as separate file."""
import logging
import pycnfg


CNFG = {
    'path': {
        'default': {
            'init': pycnfg.utils.find_path,
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        },
    },
    'logger': {
        'default': {
            'init': logging.getLogger('default'),
            'producer': pycnfg.Producer,
            'global': {},
            'patch': {},
            'priority': 1,
            'steps': [],
        },
    },
}
