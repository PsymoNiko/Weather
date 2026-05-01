#!/usr/bin/env python3
"""
GitHub PR Labeler - Automatically label pull requests based on changed files.

Uses environment variables set by GitHub Actions:
- GITHUB_REPOSITORY: owner/repo
- GITHUB_TOKEN: GitHub token
- GITHUB_EVENT_PATH: path to the PR event payload
"""

import os
import yaml
import sys
from github import Github
# from pathlib import Path
from typing import Dict, Set


def load_config(config_path: str = ".github/labeler_config.yaml") -> Dict:
    """Load label rules from YAML config."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def get_pr_number() -> int:
    """Extract PR number from GitHub event file."""
    event_path = os.environ["GITHUB_EVENT_PATH"]
    with open(event_path, "r") as f:
        import json
        event = json.load(f)
    return event["pull_request"]["number"]


def get_changed_files(token: str, repo_name: str, pr_number: int) -> Set[str]:
    """Use GitHub API to get list of files changed in the PR."""
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    files = [f.filename for f in pr.get_files()]
    return set(files)


def determine_labels(changed_files: Set[str], rules: Dict) -> Set[str]:
    """
    Determine which labels to apply based on changed files and rules.
    Rules format:
        label_name:
          - changed-files:
              - any-glob-to-any-file: "src/**/*"
          - changed-files:
              - any-glob-to-all-files: "tests/**/*"
    """
    matched_labels = set()
    for label, condition in rules.items():
        # We support only "any-glob-to-any-file" for simplicity
        if "changed-files" in condition:
            globs = condition["changed-files"].get("any-glob-to-any-file", [])
            if not globs and "any-glob-to-all-files" in condition["changed-files"]:
                # For simplicity, treat any-glob-to-all-files similarly
                globs = condition["changed-files"]["any-glob-to-all-files"]
            # Convert list to single-item list if string
            if isinstance(globs, str):
                globs = [globs]
            # Check if any changed file matches any glob
            from fnmatch import fnmatch
            for file in changed_files:
                for pattern in globs:
                    if fnmatch(file, pattern):
                        matched_labels.add(label)
                        break
                else:
                    continue
                break
    return matched_labels


def apply_labels(token: str, repo_name: str, pr_number: int, labels: Set[str]) -> None:
    """Add labels to the PR using GitHub API."""
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    # Get existing labels
    existing = {label.name for label in pr.get_labels()}
    # Add new labels
    for label in labels:
        if label not in existing:
            try:
                pr.add_to_labels(label)
                print(f"✅ Added label: {label}")
            except Exception as e:
                print(f"⚠️ Failed to add label '{label}': {e}")
    # Optional: remove labels that are no longer matched? Usually not desired.
    # We'll leave them as is – manual or another workflow can clean up.


def main():
    # Read environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ Missing GITHUB_TOKEN environment variable")
        sys.exit(1)
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    if not repo_name:
        print("❌ Missing GITHUB_REPOSITORY")
        sys.exit(1)

    # Load config
    try:
        rules = load_config()
    except FileNotFoundError:
        print("❌ labeler_config.yaml not found in .github/")
        sys.exit(1)

    pr_number = get_pr_number()
    changed_files = get_changed_files(token, repo_name, pr_number)
    print(f"📝 Changed files in PR #{pr_number}:")
    for f in sorted(changed_files):
        print(f"   {f}")

    labels = determine_labels(changed_files, rules)
    print(f"🏷️  Suggested labels: {labels or '(none)'}")

    if labels:
        apply_labels(token, repo_name, pr_number, labels)
    else:
        print("ℹ️ No labels match, skipping.")


if __name__ == "__main__":
    main()