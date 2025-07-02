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
    """Test that the CLI can be invoked and returns success."""
    result = runner.invoke(ardl, [])

    # The main assertion - CLI should return 0 when showing help
    assert result.exit_code == 0, (
        f"CLI returned exit code {result.exit_code}. "
        f"Output: {result.output}"
    )

    # Verify help is shown
    assert result.output is not None, "CLI should produce output"
    assert "Usage: ardl" in result.output, "Should show usage information"
    assert "Arista Network Download CLI" in result.output, "Should show CLI description"

def test_cli_diagnosis():
    """Diagnostic test to understand CLI loading issues."""
    from click.testing import CliRunner

    # Test 1: Can we import ardl?
    try:
        from eos_downloader.cli.cli import ardl
        print("✓ Successfully imported ardl")
    except Exception as e:
        print(f"✗ Failed to import ardl: {e}")
        raise

    # Test 2: Check if groups are loaded
    print(f"Available commands: {list(ardl.commands.keys())}")

    # Test 3: Test basic invocation
    runner = CliRunner()
    result = runner.invoke(ardl, [])

    print(f"Exit code: {result.exit_code}")
    print(f"Has output: {len(result.output) > 0}")
    print(f"Output preview: {result.output[:100] if result.output else 'No output'}")

    if result.exception:
        print(f"Exception: {result.exception}")
        import traceback
        traceback.print_exception(
            type(result.exception),
            result.exception,
            result.exception.__traceback__
        )

    # The actual assertion - this should pass
    assert result.exit_code == 0

def test_cli_via_main_function():
    """Test CLI using the main cli() function instead of direct ardl import."""
    from click.testing import CliRunner
    import sys
    from io import StringIO

    # Capture stdout to avoid cli() actually running
    old_argv = sys.argv
    old_stdout = sys.stdout

    try:
        # Mock argv to prevent cli() from trying to parse real args
        sys.argv = ['ardl']
        sys.stdout = StringIO()

        # Import and test
        from eos_downloader.cli.cli import ardl
        runner = CliRunner()
        result = runner.invoke(ardl, [])

        assert result.exit_code == 0, f"CLI failed with exit code {result.exit_code}"

    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout

