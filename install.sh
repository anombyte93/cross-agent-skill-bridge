#!/usr/bin/env bash
# cross-agent-skill-bridge installer — one command, any agent.
#   curl -fsSL https://raw.githubusercontent.com/anombyte93/cross-agent-skill-bridge/main/install.sh | bash
#
# Clones the repo, symlinks the skill into the neutral ~/.agents/skills hub
# (discovered natively by Codex/Gemini/etc.), and runs a smoke test.
# Idempotent: re-running updates in place. Never deletes your skills.
set -euo pipefail

REPO="${CROSS_AGENT_SKILL_BRIDGE_REPO:-https://github.com/anombyte93/cross-agent-skill-bridge.git}"
DEST="${CROSS_AGENT_SKILL_BRIDGE_HOME:-$HOME/.local/share/cross-agent-skill-bridge}"
HUB="$HOME/.agents/skills"
SKILL_SRC="$DEST/skills/cross-agent-skill-bridge"

command -v git >/dev/null 2>&1     || { echo "error: git is required" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "error: python3 is required" >&2; exit 1; }

if [ -d "$DEST/.git" ]; then
  echo "Updating existing install at $DEST ..."
  git -C "$DEST" pull --ff-only --quiet
else
  echo "Cloning into $DEST ..."
  rm -rf "$DEST"
  git clone --depth 1 --quiet "$REPO" "$DEST"
fi

mkdir -p "$HUB"
ln -sfn "$SKILL_SRC" "$HUB/cross-agent-skill-bridge"
echo "Linked skill -> $HUB/cross-agent-skill-bridge"

echo
echo "Smoke test (skill_bridge.py status):"
echo "----------------------------------------"
python3 "$SKILL_SRC/scripts/skill_bridge.py" status
echo "----------------------------------------"
echo
echo "Installed. Restart your agent to discover the skill, or run the CLI directly:"
echo "  python3 $SKILL_SRC/scripts/skill_bridge.py status"
