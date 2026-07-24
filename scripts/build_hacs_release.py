#!/usr/bin/env python3
"""Build a fork-aware HACS release zip for midea_ac_lan.

The source manifest keeps a normal development pin for ``midea-local``.
For release assets, we rewrite that requirement to a wheel hosted in the same
GitHub owner's ``midealocal`` repository so that forks stay self-contained.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT_DIR = ROOT / "custom_components" / "midea_ac_lan"
MANIFEST_PATH = COMPONENT_DIR / "manifest.json"
DIST_DIR = ROOT / "dist"
ZIP_PATH = DIST_DIR / "midea_ac_lan.zip"

DEFAULT_REPOSITORY = "linuxct/midea_ac_lan"
DEFAULT_LIBRARY_OWNER = "linuxct"
DEFAULT_LIBRARY_REPOSITORY = "midealocal"


def _get_requirement_version(requirements: list[str]) -> str:
    for requirement in requirements:
        if requirement.startswith("midea-local=="):
            return requirement.removeprefix("midea-local==")
    raise ValueError("manifest.json must include a 'midea-local==<version>' requirement")


def _wheel_url(owner: str, repository: str, version: str) -> str:
    wheel_name = f"midea_local-{version}-py3-none-any.whl"
    return (
        f"https://github.com/{owner}/{repository}/releases/download/"
        f"v{version}/{wheel_name}"
    )


def _validate_url(url: str) -> None:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=15):
            return
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Dependency asset check failed for {url}: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Dependency asset check failed for {url}: {exc.reason}") from exc


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPOSITORY)
    repository_owner = os.environ.get(
        "GITHUB_REPOSITORY_OWNER",
        repository.split("/", 1)[0] if "/" in repository else DEFAULT_LIBRARY_OWNER,
    )
    library_repository = os.environ.get(
        "MIDEALOCAL_REPOSITORY",
        DEFAULT_LIBRARY_REPOSITORY,
    )
    skip_validation = os.environ.get("SKIP_MIDEALOCAL_ASSET_CHECK") == "1"

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    library_version = _get_requirement_version(manifest["requirements"])
    dependency_url = _wheel_url(repository_owner, library_repository, library_version)

    if not skip_validation:
        _validate_url(dependency_url)

    manifest["requirements"] = [f"midea-local @ {dependency_url}"]
    manifest["documentation"] = f"https://github.com/{repository}#readme"
    manifest["issue_tracker"] = f"https://github.com/{repository}/issues"

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="midea_ac_lan_release_") as temp_dir:
        staged_component = Path(temp_dir) / "midea_ac_lan"
        shutil.copytree(COMPONENT_DIR, staged_component)
        (staged_component / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(staged_component.rglob("*")):
                if path.is_dir():
                    continue
                archive.write(path, path.relative_to(staged_component))

    print(f"Built {ZIP_PATH}")
    print(f"Embedded midea-local dependency: {dependency_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
