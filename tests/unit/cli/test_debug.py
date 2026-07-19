import pytest
from typer.testing import CliRunner
from eos_downloader.cli.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_debug_help(runner):
    result = runner.invoke(app, ["debug", "--help"])
    assert result.exit_code == 0
    assert "Debug commands to work with ardl" in result.output
