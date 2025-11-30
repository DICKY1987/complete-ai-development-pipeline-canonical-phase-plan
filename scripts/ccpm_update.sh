#!/usr/bin/env bash
# DOC_LINK: DOC-SCRIPT-CCPM-UPDATE-280
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
RUNTIME_DIR="$ROOT_DIR/pm"

if [[ ! -d "$RUNTIME_DIR" ]]; then
  echo "[pm:update] PM not present; installing"
  "$(dirname "$0")/ccpm_install.sh"
  exit $?
fi

TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t ccpm)
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

SRC="$TMPDIR/src"
git clone --depth 1 https://github.com/automazeio/ccpm.git "$SRC" >/dev/null 2>&1 || {
  echo "[pm:update] git clone failed" >&2
  exit 1
}

PAYLOAD="$SRC/ccpm"
if [[ ! -d "$PAYLOAD" ]]; then
  echo "[pm:update] Unexpected repository layout; expected /ccpm subdir" >&2
  exit 1
}

for d in scripts commands rules agents context hooks prds epics; do
  if [[ -e "$PAYLOAD/$d" ]]; then
    rm -rf "$RUNTIME_DIR/$d"
    cp -R "$PAYLOAD/$d" "$RUNTIME_DIR/"
  fi
done

if [[ -d "$RUNTIME_DIR/scripts/pm" ]]; then
  echo "[pm:update] Updated PM runtime at $RUNTIME_DIR"
else
  echo "[pm:update] pm scripts not found after update" >&2
  exit 1
fi
