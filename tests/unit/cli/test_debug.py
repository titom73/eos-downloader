
import pytest
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl

@pytest.fixture
def runner():
    return CliRunner()

def test_debug_help(runner):
    result = runner.invoke(ardl, ['debug', '--help'])
    assert result.exit_code == 0
    assert "Debug commands to work with ardl" in result.output