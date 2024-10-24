import pytest

from dot_tools.misc_tools import setup_logging


@pytest.yield_fixture(scope='session', autouse=True)
def setup():
    setup_logging(verbose=True)
