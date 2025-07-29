#!/usr/bin/env python3
"""
Script to update the coverage badge in README.md with actual coverage percentage.
"""

import re
import subprocess
import sys
from pathlib import Path


def get_coverage_percentage():
    """Get the coverage percentage from coverage report."""
    try:
        # Run coverage report and capture output
        result = subprocess.run(
            ["coverage", "report", "--format=total"],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the percentage
        coverage_str = result.stdout.strip()
        if coverage_str.isdigit():
            return int(coverage_str)
        else:
            # Try to parse from regular coverage report
            result = subprocess.run(
                ["coverage", "report"],
                capture_output=True,
                text=True,
                check=True
            )

            # Look for TOTAL line
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('TOTAL'):
                    # Extract percentage from line like "TOTAL    1046   1046     0%"
                    parts = line.split()
                    if parts and parts[-1].endswith('%'):
                        return int(parts[-1][:-1])

        return 0

    except subprocess.CalledProcessError:
        print("Error running coverage command")
        return 0
    except Exception as e:
        print(f"Error getting coverage: {e}")
        return 0


def generate_coverage_badge_url(percentage):
    """Generate a coverage badge URL based on percentage."""
    if percentage >= 80:
        color = "brightgreen"
    elif percentage >= 60:
        color = "yellow"
    elif percentage >= 40:
        color = "orange"
    else:
        color = "red"

    return f"https://img.shields.io/badge/coverage-{percentage}%25-{color}"


def update_readme_badge(coverage_percentage, readme_path=None):
    """Update the coverage badge in README.md.

    Args:
        coverage_percentage: The coverage percentage to display
        readme_path: Path to README.md file (optional, defaults to repository root)
    """
    if readme_path is None:
        readme_path = Path(__file__).parent.parent / "README.md"
    else:
        readme_path = Path(readme_path)

    if not readme_path.exists():
        print(f"README.md not found at {readme_path}")
        return False

    # Read current README
    content = readme_path.read_text(encoding='utf-8')

    # Generate new badge URL
    badge_url = generate_coverage_badge_url(coverage_percentage)

    # Pattern to match existing coverage badge
    pattern = r'!\[Coverage\]\(https://.*?coverage.*?\)'

    # Replacement
    replacement = f'![Coverage]({badge_url})'

    # Replace or add badge
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
    else:
        # If no existing coverage badge, add it after the tests badge
        tests_badge_pattern = r'(\[!\[tests\].*?\)\n)'
        if re.search(tests_badge_pattern, content):
            new_content = re.sub(
                tests_badge_pattern,
                f'\\1{replacement}\n',
                content
            )
        else:
            print("Could not find place to insert coverage badge")
            return False

    # Write updated content
    readme_path.write_text(new_content, encoding='utf-8')
    print(f"Updated README.md with coverage: {coverage_percentage}%")
    return True


def main():
    """Main function."""
    # Get coverage percentage
    coverage = get_coverage_percentage()
    print(f"Current coverage: {coverage}%")

    # Update README
    # Define path to README at repository root
    readme_path = Path(__file__).parent.parent.parent / "README.md"

    # Update README with the explicit path
    if update_readme_badge(coverage, readme_path):
        print(f"Successfully updated README.md at {readme_path}")
        sys.exit(0)
    else:
        print(f"Failed to update README.md at {readme_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
