
import pytest
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl

@pytest.fixture
def runner():
    return CliRunner()

def test_info_help(runner):
    result = runner.invoke(ardl, ['info', '--help'])
    assert result.exit_code == 0
    assert "List information from Arista website" in result.output