#!/usr/bin/env python3
"""Fetch upstream README files listed in docs/sources-manifest.yaml.

For each entry in the manifest, downloads the README from the specified
GitHub repo/branch and writes it into docs/Sources/ with a header comment
indicating its origin.

Exit code 0 if all fetches succeed; 1 if any fail.
"""

import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Paths (relative to the repository root)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
MANIFEST_PATH = REPO_ROOT / "docs" / "sources-manifest.yaml"
OUTPUT_DIR = REPO_ROOT / "docs" / "Sources"

RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/{repo}/{branch}/README.md"
HEADER_TEMPLATE = "<!-- Auto-generated from https://github.com/{repo} — do not edit manually -->\n\n"


def load_manifest(path: Path) -> list[dict]:
    """Read the YAML manifest and return the list of source entries."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    sources = data.get("sources")
    if not sources:
        print(f"ERROR: No 'sources' key found in {path}", file=sys.stderr)
        sys.exit(1)
    return sources


def fetch_readme(repo: str, branch: str) -> str:
    """Download the README.md content from a GitHub repo."""
    url = RAW_URL_TEMPLATE.format(repo=repo, branch=branch)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def main() -> None:
    sources = load_manifest(MANIFEST_PATH)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fetched = 0
    failed = 0
    errors: list[str] = []

    for entry in sources:
        repo = entry["repo"]
        branch = entry["branch"]
        filename = entry["filename"]
        dest = OUTPUT_DIR / filename

        try:
            content = fetch_readme(repo, branch)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as exc:
            failed += 1
            msg = f"FAILED  {repo} -> {filename}: {exc}"
            errors.append(msg)
            print(msg, file=sys.stderr)
            continue

        header = HEADER_TEMPLATE.format(repo=repo)
        dest.write_text(header + content, encoding="utf-8")
        fetched += 1
        print(f"OK      {repo} -> docs/Sources/{filename}")

    # Summary
    print()
    print(f"Fetched: {fetched}  Failed: {failed}  Total: {fetched + failed}")

    if failed:
        print("\nErrors:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
