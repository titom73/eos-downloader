import pytest
from click.testing import CliRunner
from eos_downloader.cli.cli import ardl

@pytest.fixture
def runner():
    return CliRunner()

def test_ardl_help(runner):
    result = runner.invoke(ardl, ['--help'])
    assert result.exit_code == 0
    assert "Arista Network Download CLI" in result.output

def test_ardl_version(runner):
    result = runner.invoke(ardl, ['--version'])
    assert result.exit_code == 0
    assert "version" in result.output

def test_cli_execution(runner):
    result = runner.invoke(ardl, [])
    assert result.exit_code == 0
    assert "Usage: ardl [OPTIONS] COMMAND [ARGS]..." in result.output
    assert "Arista Network Download CLI" in result.output

