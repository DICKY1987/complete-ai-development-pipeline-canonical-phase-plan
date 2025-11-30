#!/usr/bin/env bash
# DOC_LINK: DOC-SCRIPT-WORKTREE-START-288
set -euo pipefail

EPIC_NAME="${1:-}"
BRANCH_NAME="${2:-}"
if [[ -z "$EPIC_NAME" ]]; then
  echo "usage: $0 <epic-name> [branch-name]" >&2
  exit 2
fi

# repo root
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$ROOT" ]]; then
  ROOT=$(pwd)
fi

BRANCH="${BRANCH_NAME:-epic/${EPIC_NAME}}"
WT_PATH="$(dirname "$ROOT")/epic-${EPIC_NAME}"

if command -v git >/dev/null 2>&1; then
  echo "[worktree] Adding worktree at $WT_PATH (branch $BRANCH)"
  (cd "$ROOT" && git worktree add "$WT_PATH" -b "$BRANCH")
else
  echo "[worktree] git not found. Creating directory only: $WT_PATH"
  mkdir -p "$WT_PATH"
fi

echo "[worktree] Ready: $WT_PATH"

