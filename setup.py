"""A setuptools based module setup."""


import os
import setuptools


NAME = "pycnfg"
DESCRIPTION = "Pycnfg. Flexible Python configurations."
URL = "https://github.com/nizaevka/pycnfg"
REQUIRES_PYTHON = ">=3.6"
PATH = os.path.abspath(os.path.dirname(__file__))


# Get text.
def parse_text(filename, splitlines=False):
    with open(os.path.join(PATH, filename), "r", encoding='utf-8') as f:
        if splitlines:
            return f.read().splitlines()
        else:
            return f.read()


# Get version.
version = {}
with open("src/{}/__version__.py".format(NAME)) as fp:
    exec(fp.read(), version)


# Prevent install dependencies for readthedoc build
# (there is no way to set --no-deps in pip install).
on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd and False:
    INSTALL_REQUIRES = []
else:
    INSTALL_REQUIRES = parse_text('requirements.txt', splitlines=True)


setuptools.setup(
    name=NAME,
    version=version['__version__'],
    author="nizaevka",
    author_email="knizaev@gmail.com",
    description="Flexible Python configurations.",
    keywords='configuration',
    long_description=parse_text('README.md', splitlines=False),
    long_description_content_type="text/markdown",
    url=URL,
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    install_requires=INSTALL_REQUIRES,
    # $ pip install package[dev]
    extras_require={
        'dev': parse_text('requirements_dev.txt', splitlines=True),
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=REQUIRES_PYTHON,
    project_urls={
        'Documentation': 'https://pycnfg.readthedocs.io/',
        'Source': "https://github.com/nizaevka/pycnfg",
        'Tracker': "https://github.com/nizaevka/pycnfg/issues",
    },
)
