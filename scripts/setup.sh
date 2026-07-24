#!/usr/bin/env bash
#
# One-time development environment setup, powered by uv.
# Prerequisite: install uv -> https://docs.astral.sh/uv/getting-started/installation/
#   macOS/Linux/WSL2: curl -LsSf https://astral.sh/uv/install.sh | sh
#   Windows:          powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

set -e

cd "$(dirname "$0")/.."

# Create the virtualenv (.venv) and install the project + dev dependency group.
# uv automatically downloads the Python version pinned in .python-version if needed.
uv sync

# When developing the integration and the library together, prefer a sibling
# checkout of midea-local/midealocal over the PyPI fallback pinned in pyproject.
for candidate in ../midea-local ../midealocal; do
    if [ -f "$candidate/setup.py" ]; then
        echo "Installing sibling midea-local checkout from $candidate"
        uv pip install --reinstall -e "$candidate"
        break
    fi
done

# Install the git hooks (pre-commit + commit-msg for Conventional Commits).
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

echo
echo "Setup complete. Run Home Assistant with: ./scripts/run.sh"
