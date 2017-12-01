import pytest
import yaml


@pytest.fixture
def testpath(request):
    return request.config.getoption("--testpath")


@pytest.fixture
def testname(request):
    return request.config.getoption("--testname")


def pytest_addoption(parser):
    parser.addoption(
        "--testname", action="store", default=None,
        help="test name to run (Default to None which will run all tests)")
    parser.addoption(
        "--testpath", action="store", default=None,
        help="path to directory holding test yaml")
