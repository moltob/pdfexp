"""Common fixtures and configurations for this test directory."""
import os

import pytest


@pytest.fixture('module', autouse=True)
def cwd_module_dir():
    """Change current directory to this module's folder to access inputs and write outputs."""
    cwd = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    yield
    os.chdir(cwd)
