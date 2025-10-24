#!/usr/bin/env python3
"""
Sync Python versions between .github/python-versions.json and pyproject.toml

This script ensures that the Python versions used in GitHub Actions workflows
match the versions specified in pyproject.toml.
"""

import json
import re
import sys
from pathlib import Path
from typing import List


def load_python_versions_from_json(json_path: Path) -> dict:
    """Load Python versions from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_pyproject_classifiers(
    pyproject_path: Path,
    versions: List[str]
) -> None:
    """Update Python version classifiers in pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")

    # Remove all existing Python X.Y classifiers (e.g., 'Programming Language :: Python :: 3.9')
    # But keep 'Programming Language :: Python :: 3' and 'Programming Language :: Python :: 3 :: Only'
    pattern = r"  'Programming Language :: Python :: \d+\.\d+'[,\n]+"
    content_cleaned = re.sub(pattern, "", content)

    # Now insert new classifiers after 'Programming Language :: Python :: 3'
    # Find the line with this classifier
    insertion_marker = "'Programming Language :: Python :: 3'"
    insertion_pos = content_cleaned.find(insertion_marker)

    if insertion_pos == -1:
        print("❌ Could not find 'Programming Language :: Python :: 3' in pyproject.toml")
        sys.exit(1)

    # Find the end of that line (after the comma)
    end_of_line = content_cleaned.find('\n', insertion_pos)
    if end_of_line == -1:
        end_of_line = len(content_cleaned)

    # Sort versions for consistent ordering
    sorted_versions = sorted(versions)

    # Generate new classifier lines with proper indentation
    new_lines = []
    for version in sorted_versions:
        new_lines.append(f"  'Programming Language :: Python :: {version}',")

    # Insert new classifiers
    new_content = (
        content_cleaned[:end_of_line + 1] +
        '\n'.join(new_lines) + '\n' +
        content_cleaned[end_of_line + 1:]
    )

    pyproject_path.write_text(new_content, encoding="utf-8")


def update_requires_python(
    pyproject_path: Path,
    min_version: str
) -> None:
    """Update requires-python in pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")

    # Pattern: requires-python = ">=X.X"
    pattern = r'requires-python\s*=\s*"[^"]*"'
    replacement = f'requires-python = ">={min_version}"'

    new_content = re.sub(pattern, replacement, content)

    pyproject_path.write_text(new_content, encoding="utf-8")


def main():
    """Main function."""
    # Get paths (script is in .github/scripts/, so go up three levels to repo root)
    repo_root = Path(__file__).parent.parent.parent
    json_path = repo_root / ".github" / "python-versions.json"
    pyproject_path = repo_root / "pyproject.toml"

    # Check if files exist
    if not json_path.exists():
        print(f"❌ {json_path} not found")
        sys.exit(1)

    if not pyproject_path.exists():
        print(f"❌ {pyproject_path} not found")
        sys.exit(1)

    # Load versions
    print("📋 Loading Python versions from JSON...")
    versions_data = load_python_versions_from_json(json_path)
    versions = versions_data["versions"]
    min_version = versions_data["min_version"]
    if not versions:
        print("❌ No Python versions found in the JSON file.")
        sys.exit(1)
    max_version = versions_data.get("max_version", versions[-1])

    print(f"✅ Found versions: {versions}")
    print(f"   Min version: {min_version}")
    print(f"   Max version: {max_version}")

    # Update pyproject.toml
    print("\n📝 Updating pyproject.toml...")

    try:
        update_pyproject_classifiers(pyproject_path, versions)
        print("✅ Updated Python version classifiers")

        update_requires_python(pyproject_path, min_version)
        print("✅ Updated requires-python")

        print("\n🎉 Synchronization complete!")
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff pyproject.toml")
        print("   2. Run tests to ensure compatibility")
        print("   3. Commit changes: git add pyproject.toml && git commit -m 'chore: sync Python versions'")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
