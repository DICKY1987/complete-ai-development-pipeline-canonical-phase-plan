#!/usr/bin/env bash
set -euo pipefail

EPIC_NAME="${1:-}"
BRANCH_NAME="${2:-}"
if [[ -z "$EPIC_NAME" ]]; then
  echo "usage: $0 <epic-name> [branch-name]" >&2
  exit 2
fi

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [[ -z "$ROOT" ]]; then
  echo "[worktree] git repo not found; skipping merge" >&2
  exit 0
fi

BRANCH="${BRANCH_NAME:-epic/${EPIC_NAME}}"
echo "[worktree] Merging worktree branch $BRANCH into current branch"
(cd "$ROOT" && git fetch --all --prune && git merge "$BRANCH")
echo "[worktree] Merge attempted for $BRANCH"

