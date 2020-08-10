"""Test pycnfg.run util."""
import pycnfg
import pytest
import importlib.util


# Import test params.
conf = f"{__file__.replace('.py', '')}/params.py"
spec = importlib.util.spec_from_file_location(f"temp", f"{conf}")
conf_file = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conf_file)
params = conf_file.params


@pytest.mark.parametrize("id_,args,kwargs,expected", params)
def test_run(id_, args, kwargs, expected):
    objects = pycnfg.run(*args, **kwargs)
    assert objects == expected, f"test={id_}"

