#!/usr/bin/env python3
"""
Pre-commit hook to verify Python versions are synchronized.

This script checks that the Python versions in .github/python-versions.json
match the versions specified in pyproject.toml classifiers.
"""

import json
import re
import sys
from pathlib import Path
from typing import List


def load_python_versions_from_json(json_path: Path) -> List[str]:
    """Load Python versions from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["versions"]


def extract_python_versions_from_pyproject(pyproject_path: Path) -> List[str]:
    """Extract Python version classifiers from pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")

    # Pattern to match: 'Programming Language :: Python :: X.X' or "Programming Language :: Python :: X.X"
    # Handle both single and double quotes
    pattern = r'["\']Programming Language :: Python :: (\d+\.\d+)["\']'
    matches = re.findall(pattern, content)

    return matches


def main() -> int:
    """Main function."""
    # Get paths (script location: .github/scripts/check-python-versions.py)
    # Path resolution: .github/scripts/ -> .github/ -> repo root
    # Using parent.parent.parent to navigate from script to repository root
    repo_root = Path(__file__).parent.parent.parent
    json_path = repo_root / ".github" / "python-versions.json"
    pyproject_path = repo_root / "pyproject.toml"

    # Load versions from both sources
    try:
        json_versions = load_python_versions_from_json(json_path)
        pyproject_versions = extract_python_versions_from_pyproject(pyproject_path)
    except Exception as e:
        print(f"❌ Error loading versions: {e}")
        return 1

    # Normalize versions (no quote stripping needed)
    # json_versions are already clean strings from JSON
    pyproject_versions = sorted(pyproject_versions)
    json_versions_sorted = sorted(json_versions)

    # Compare
    if pyproject_versions != json_versions_sorted:
        print("❌ Python versions are out of sync!")
        print(f"\n📋 Versions in .github/python-versions.json: {json_versions_sorted}")
        print(f"📄 Versions in pyproject.toml: {pyproject_versions}")
        print("\n💡 To fix this, run:")
        print("   python .github/scripts/sync-python-versions.py")
        return 1

    print("✅ Python versions are synchronized")
    return 0


if __name__ == "__main__":
    sys.exit(main())
