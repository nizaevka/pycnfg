ALPHA UNDERCONSTRUCTED
<div align="center">

[![Mlshell logo](https://github.com/nizaevka/pycnfg/blob/master/pictures/pycnfg_logo.PNG?raw=true)](https://github.com/nizaevka/pycnfg)

**Pure Python configuration.**

[![Build Status](https://travis-ci.org/nizaevka/pycnfg.svg?branch=master)](https://travis-ci.org/nizaevka/pycnfg)
[![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/)
[![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://pycnfg.readthedocs.io/en/latest/)
[![Telegram](https://img.shields.io/badge/channel-on%20telegram-blue)](https://t.me/nizaevka)

</div>

**PyCNFG** is a lib to execute Python-based configuration:
- Flexibility.
- Pure python.

[![Workflow](https://github.com/nizaevka/pycnfg/blob/master/docs/source/_static/images/workflow.JPG?raw=true)]

For details, please refer to
 [Concepts](https://pycnfg.readthedocs.io/en/latest/Concepts.html>).

--

## Installation

#### PyPi [![PyPi version](https://img.shields.io/pypi/v/pycnfg.svg)](https://pypi.org/project/pycnfg/) [![PyPI Status](https://pepy.tech/badge/pycnfg)](https://pepy.tech/project/pycnfg)

```bash
pip install -U pycnfg
```

<details>
<summary>Specific versions with additional requirements</summary>
<p>

```bash
pip install catalyst[dev]        # installs dependencies for development
```
</p>
</details>

#### Docker [![Docker Pulls](https://img.shields.io/docker/pulls/nizaevka/pycnfg)](https://hub.docker.com/r/nizaevka/pycnfg/tags)

```bash
docker run -it nizaevka/pycnfg
```

MLshell is compatible with: Python 3.6+.


## Getting started

```python
import pycnfg
```
see Docs for details ;)

## Docs and examples
An overview and API documentation can be found here
[![Docs](https://readthedocs.org/projects/pycnfg/badge/?version=latest)](https://readthedocs.org/pycnfg/en/latest/?badge=latest)

Check **[examples folder](examples)** of the repository:
- For regression example please follow [Allstate claims severity](examples/regression).
- For classification example please follow [IEEE-CIS Fraud Detection](examples/classification).

## Contribution guide

We appreciate all contributions.
If you are planning to contribute back bug-fixes,
please do so without any further discussion.
If you plan to contribute new features, utility functions or extensions,
please first open an issue and discuss the feature with us.

- Please see the [contribution guide](CONTRIBUTING.md) for more information.
- By participating in this project, you agree to abide by its [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the Apache License, Version 2.0 see the [LICENSE](LICENSE) file for details
[![License](https://img.shields.io/github/license/nizaevka/pycnfg.svg)](LICENSE)