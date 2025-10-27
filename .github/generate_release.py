#!/usr/bin/env python
"""generate_release.py.

This script is used to generate the release.yml file as per
https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes
"""

import os
import re
import yaml


def parse_workflow_types_and_scopes(workflow_path: str):
    """Parse `types` and `scopes` from the pr-triage workflow file.

    Returns (types_list, scopes_list). Falls back to defaults when parsing fails.
    """
    default_types = [
        "feat",
        "fix",
        "cut",
        "doc",
        "ci",
        "bump",
        "test",
        "refactor",
        "revert",
        "make",
        "chore",
    ]
    default_scopes = ["eos_downloader", "eos_downloader.cli"]

    if not os.path.exists(workflow_path):
        return default_types, default_scopes

    types = []
    scopes = []
    with open(workflow_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Parse types: | block (YAML literal block scalar)
    # Look for 'types: |' followed by indented lines
    match_types = re.search(r"\btypes:\s*\|\s*\n((?:\s+\S+\n)+)", content)
    if match_types:
        for line in match_types.group(1).splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                types.append(line)

    # Parse scopes: | block
    match_scopes = re.search(r"\bscopes:\s*\|\s*\n((?:\s+\S+\n)+)", content)
    if match_scopes:
        for line in match_scopes.group(1).splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                scopes.append(line)

    return (types or default_types, scopes or default_scopes)


# Types that should be excluded from release notes
EXCLUDED_TYPES = {"ci", "test"}

# Types that can indicate breaking changes when marked with '!'
# Exclude types that are typically excluded or non-impactful
BREAKING_CHANGE_TYPES = {
    "feat", "fix", "cut", "revert", "refactor", "bump"
}

# CI and Test are excluded from Release Notes
CATEGORIES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "cut": "Cut",
    "doc": "Documentation",
    "bump": "Bump",
    "revert": "Revert",
    "refactor": "Refactoring",
}


class SafeDumper(yaml.SafeDumper):
    """Make yamllint happy
    https://github.com/yaml/pyyaml/issues/234#issuecomment-765894586.
    """

    # pylint: disable=R0901

    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


if __name__ == "__main__":
    exclude_list = []
    categories_list = []

    # Discover types and scopes from the pr-triage workflow (fallback to defaults)
    workflow_path = os.path.join(os.path.dirname(__file__), "workflows", "pr-triage.yml")
    types_list, SCOPES = parse_workflow_types_and_scopes(workflow_path)

    # Exclude configured types from release notes
    # Labels are separate: kind:test AND scope:xxx, not kind:test(xxx)
    for excluded_type in EXCLUDED_TYPES:
        if excluded_type in types_list:
            exclude_list.append(f"kind:{excluded_type}")

    # Build breaking changes labels from parsed types
    # GitHub release notes matches if ANY label in the list is present
    # Since we use separate labels (kind: and scope:), we only list kind: labels
    # Breaking changes are detected by the '!' marker in PR title and labeled with compat:breaking
    breaking_labels = ["compat:breaking"]

    categories_list.append(
        {
            "title": "Breaking Changes",
            "labels": breaking_labels,
        },
    )

    # Add new features
    feat_labels = []
    if "feat" in types_list:
        feat_labels.append("kind:feat")

    categories_list.append(
        {
            "title": "New features and enhancements",
            "labels": feat_labels,
        },
    )

    # Add fixes
    fixes_labels = []
    if "fix" in types_list:
        fixes_labels.append("kind:fix")

    categories_list.append(
        {
            "title": "Fixed issues",
            "labels": fixes_labels,
        },
    )

    # Add Documentation
    doc_labels = []
    if "doc" in types_list:
        doc_labels.append("kind:doc")

    categories_list.append(
        {
            "title": "Documentation",
            "labels": doc_labels,
        },
    )

    # Add the catch all
    categories_list.append(
        {
            "title": "Other Changes",
            "labels": ["*"],
        },
    )

    # Generate .github/release.yml (GitHub reads this file for auto-generated release notes)
    output_path = os.path.join(os.path.dirname(__file__), "release.yml")
    with open(output_path, "w", encoding="utf-8") as release_file:
        yaml.dump(
            {
                "changelog": {
                    "exclude": {"labels": exclude_list},
                    "categories": categories_list,
                },
            },
            release_file,
            Dumper=SafeDumper,
            sort_keys=False,
        )
