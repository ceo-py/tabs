#!/bin/bash
# ---------------------------------------------------------------------------
# TABS 90 — pull the latest site from GitHub into the web root.
#
# Installed on the VPS as /home/ceo/production/tabs-deploy.sh and driven by
# the user crontab (every 5 minutes) — no root needed.
# ---------------------------------------------------------------------------
set -uo pipefail

REPO=/home/ceo/production/tabs-repo
DEST=/home/ceo/production/tabs
LOG=/home/ceo/production/deploy.log

{
  echo "=== deploy $(date -Is) ==="

  if [ ! -d "$REPO/.git" ]; then
    echo "repo missing, cloning"
    rm -rf "$REPO"
    GIT_TERMINAL_PROMPT=0 git clone --quiet https://github.com/ceo-py/tabs.git "$REPO" || {
      echo "clone failed"; exit 1; }
  else
    GIT_TERMINAL_PROMPT=0 git -C "$REPO" pull --ff-only --quiet || {
      echo "pull failed"; exit 1; }
  fi

  mkdir -p "$DEST"
  # replace the generated trees so removed songs disappear as well
  rm -rf "$DEST/cards" "$DEST/thumbs" "$DEST/data"
  tar -C "$REPO/site" -cf - . | tar -C "$DEST" -xf -

  echo "ok: $(git -C "$REPO" rev-parse --short HEAD)  ($(find "$DEST" -name '*.webp' | wc -l) webp files)"
} >>"$LOG" 2>&1
