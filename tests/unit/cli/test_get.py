
import pytest
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl

@pytest.fixture
def runner():
    return CliRunner()

def test_get_help(runner):
    result = runner.invoke(ardl, ['get', '--help'])
    assert result.exit_code == 0
    assert "Download Arista from Arista website" in result.output