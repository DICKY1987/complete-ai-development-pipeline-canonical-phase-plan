#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
RUNTIME_DIR="$ROOT_DIR/ccpm"

if [[ ! -d "$RUNTIME_DIR" ]]; then
  echo "[ccpm:update] CCPM not present; installing"
  "$(dirname "$0")/ccpm_install.sh"
  exit $?
fi

TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t ccpm)
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

SRC="$TMPDIR/src"
git clone --depth 1 https://github.com/automazeio/ccpm.git "$SRC" >/dev/null 2>&1 || {
  echo "[ccpm:update] git clone failed" >&2
  exit 1
}

PAYLOAD="$SRC/ccpm"
if [[ ! -d "$PAYLOAD" ]]; then
  echo "[ccpm:update] Unexpected repository layout; expected /ccpm subdir" >&2
  exit 1
}

for d in scripts commands rules agents context hooks prds epics; do
  if [[ -e "$PAYLOAD/$d" ]]; then
    rm -rf "$RUNTIME_DIR/$d"
    cp -R "$PAYLOAD/$d" "$RUNTIME_DIR/"
  fi
done

if [[ -d "$RUNTIME_DIR/scripts/pm" ]]; then
  echo "[ccpm:update] Updated CCPM runtime at $RUNTIME_DIR"
else
  echo "[ccpm:update] pm scripts not found after update" >&2
  exit 1
fi

