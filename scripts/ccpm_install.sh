#!/usr/bin/env bash
set -euo pipefail

# Install CCPM runtime into ./ccpm (scripts, commands, rules, agents, ...)

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
RUNTIME_DIR="$ROOT_DIR/ccpm"

if [[ -d "$RUNTIME_DIR/scripts/pm" ]]; then
  echo "[ccpm:install] CCPM already present at $RUNTIME_DIR"
  exit 0
fi

TMPDIR=$(mktemp -d 2>/dev/null || mktemp -d -t ccpm)
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

SRC="$TMPDIR/src"

if command -v git >/dev/null 2>&1; then
  echo "[ccpm:install] Cloning automazeio/ccpm"
  git clone --depth 1 https://github.com/automazeio/ccpm.git "$SRC" >/dev/null 2>&1
else
  echo "[ccpm:install] git not found; downloading ZIP"
  curl -sSL -o "$TMPDIR/ccpm.zip" https://codeload.github.com/automazeio/ccpm/zip/refs/heads/main
  mkdir -p "$SRC"
  unzip -q "$TMPDIR/ccpm.zip" -d "$TMPDIR"
  mv "$TMPDIR"/ccpm-* "$SRC"
fi

PAYLOAD="$SRC/ccpm"
if [[ ! -d "$PAYLOAD" ]]; then
  echo "[ccpm:install] Unexpected repository layout; expected /ccpm subdir" >&2
  exit 1
fi

mkdir -p "$RUNTIME_DIR"
for d in scripts commands rules agents context hooks prds epics; do
  if [[ -e "$PAYLOAD/$d" ]]; then
    cp -R "$PAYLOAD/$d" "$RUNTIME_DIR/"
  fi
done

if [[ -d "$RUNTIME_DIR/scripts/pm" ]]; then
  echo "[ccpm:install] Installed CCPM runtime at $RUNTIME_DIR"
else
  echo "[ccpm:install] pm scripts not found after install" >&2
  exit 1
fi

