<div align="center">

<!-- relative to branch (PyPi not recognize)
Possible PyPi add support soon https://github.com/pypa/readme_renderer/issues/163
[![Pycnfg logo](docs/source/_static/images/logo.png?raw=true)](https://github.com/nizaevka/pycnfg)
-->
[![Pycnfg logo](https://github.com/nizaevka/pycnfg/blob/master/docs/source/_static/images/logo.png?raw=true)](https://github.com/nizaevka/pycnfg)

**Flexible Python configurations.**

[![Build Status](https://travis-ci.org/nizaevka/pycnfg.svg?branch=master)](https://travis-ci.org/nizaevka/pycnfg)
[![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/)
[![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://pycnfg.readthedocs.io/en/latest/)
[![Telegram](https://img.shields.io/badge/channel-on%20telegram-blue)](https://t.me/nizaevka)

</div>

**Pycnfg** is a tool to execute Python-based configuration.
- Pure Python.
- Flexible.

It offers unified patten to create arbitrary Python objects pipeline-wise. 
That naturally allows to control all parameters via single file.

<!-- relative to branch (PyPi not recognize)
![Logic](docs/source/_static/images/producer.png?raw=true)
-->
![Logic](https://github.com/nizaevka/pycnfg/blob/master/docs/source/_static/images/producer.png?raw=true)

For details, please refer to
 [Concepts](https://pycnfg.readthedocs.io/en/latest/Concepts.html).

## Installation

#### PyPi [![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/) [![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)

```bash
pip install pycnfg
```

<details>
<summary>Development installation (tests and docs) </summary>
<p>

```bash
pip install pycnfg[dev]
```
</p>
</details>

#### Docker [![Docker Pulls](https://img.shields.io/docker/pulls/nizaevka/pycnfg)](https://hub.docker.com/r/nizaevka/pycnfg/tags)

```bash
docker run -it nizaevka/pycnfg
```

Pycnfg is tested on: Python 3.6+.

## Docs
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://pycnfg.readthedocs.io/en/latest)

## Getting started

```python
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
```
see docs for details ;)

## Examples
<!--
Check **[examples folder](examples)**.
-->
Check **[examples folder](https://github.com/nizaevka/pycnfg/blob/master/examples)**.

Check also **[mlshell](https://github.com/nizaevka/mlshell)** - a ML framework based on Pycnfg.

## Contribution guide
<!--
- [contribution guide](CONTRIBUTING.md).
-->
- [contribution guide](https://github.com/nizaevka/pycnfg/blob/master/CONTRIBUTING.md).

## License
<!--
Apache License, Version 2.0 [LICENSE](LICENSE).
-->

Apache License, Version 2.0 [LICENSE](https://github.com/nizaevka/pycnfg/blob/master/LICENSE).
[![License](https://img.shields.io/github/license/nizaevka/pycnfg.svg)](LICENSE)