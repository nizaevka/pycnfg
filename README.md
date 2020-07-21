<div align="center">

[![Pycnfg logo](https://github.com/nizaevka/pycnfg/blob/master/docs/source/_static/logo.PNG?raw=true)](https://github.com/nizaevka/pycnfg)

**Flexible Python configurations.**

[![Build Status](https://travis-ci.org/nizaevka/pycnfg.svg?branch=master)](https://travis-ci.org/nizaevka/pycnfg)
[![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/)
[![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://pycnfg.readthedocs.io/en/latest/)
[![Telegram](https://img.shields.io/badge/channel-on%20telegram-blue)](https://t.me/nizaevka)

</div>

**PyCNFG** is a tool to execute Python-based configuration.
- Pure Python.
- Flexible.

It offers unified patten to create arbitrary Python objects pipeline-wise. 
That naturally allows to control all parameters via single file.

[![Workflow](https://github.com/nizaevka/pycnfg/blob/master/docs/source/_static/images/scheme.png?raw=true)]

For details, please refer to
 [Concepts](https://pycnfg.readthedocs.io/en/latest/Concepts.html>).

## Installation

#### PyPi [![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/) [![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)

```bash
pip install -U pycnfg
```

<details>
<summary>Development installation (tests and docs): </summary>
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

Pycnfg is testes on: Python 3.6+.

## Docs
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://readthedocs.org/pycnfg/en/latest/?badge=latest)

## Getting started

```python
import pycnfg

objects = pycnfg.run({})
print(objects)
```
see docs for details ;)

## Examples
Check **[examples folder](examples)**.

## Contribution guide
- [contribution guide](CONTRIBUTING.md).

## License

Apache License, Version 2.0 [LICENSE](LICENSE).
[![License](https://img.shields.io/github/license/nizaevka/pycnfg.svg)](LICENSE)