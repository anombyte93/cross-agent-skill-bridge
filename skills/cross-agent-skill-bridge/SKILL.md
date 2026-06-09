---
name: cross-agent-skill-bridge
description: Use when you want a skill (a SKILL.md directory) authored for one coding agent to be available in another — Claude Code, Codex, Gemini, etc. — or to see which skills exist in which agents and where copies have diverged. Hub-and-spoke sync via the neutral ~/.agents/skills directory. Selective and non-destructive: never silently overwrites a diverged copy, never deletes the source.
metadata:
  user-invocable: true
---

# Cross-Agent Skill Bridge

**Core principle:** Coding agents read skills from different directories (`~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`, `~/.gemini/skills`). Author a skill once, then **bridge** it to the others — selectively, and without clobbering anything you've changed elsewhere.

`~/.agents/skills/` is the neutral **hub** that multiple agents discover natively; each agent dir is a **spoke**. This skill drives `scripts/skill_bridge.py` to inspect and sync between them.

## When to use

- ✅ "Make my Claude skill `X` usable in Codex too."
- ✅ "Which of my skills are only in one agent? Where have copies drifted apart?"
- ✅ Keep one source-of-truth skill live across agents (`--mode link`).
- ❌ Migrating MCP servers or agents (this is skills-only; see Notes).
- ❌ Deleting skills (this tool never deletes a source).

## Decide first: run `status`

Never bulk-sync blind. See the presence/divergence matrix first so you only share what you actually want (some skills may be redundant or intentionally agent-specific):

```bash
python3 scripts/skill_bridge.py status
```

Output columns are the agents; cells are content hashes. `link:<hash>` = symlink, `-` = absent, `⚠ DIVERGED` = copies differ across agents (decide which is canonical before syncing).

## Share a skill

```bash
# Preview first — changes nothing:
python3 scripts/skill_bridge.py share --from claude --skill repo-sanitize --dry-run

# Copy a named skill from Claude to all other present agents:
python3 scripts/skill_bridge.py share --from claude --skill repo-sanitize

# Or to specific targets, keeping them live via symlink:
python3 scripts/skill_bridge.py share --from claude --to hub --skill repo-sanitize --mode link

# Share everything in one agent (use after reviewing status):
python3 scripts/skill_bridge.py share --from claude --all
```

### Flags
- `--from AGENT` (required) — source agent.
- `--to AGENT` (repeatable) — targets; default is every other present agent.
- `--skill NAME` (repeatable) or `--all` — what to share.
- `--mode copy` (default) | `link` — `link` symlinks the source so edits stay in sync everywhere.
- `--force` — overwrite a target that has **diverged**. Without it, diverged targets are skipped with a warning.
- `--dry-run` — show the plan, change nothing.

## Safety rules (built in)

1. **Non-destructive by default** — a diverged target is never overwritten without `--force`. The hash compare catches "I edited this copy and forgot."
2. **Source is never deleted or modified** — bridging is one-way per invocation; the source agent's copy is read-only here.
3. **In-sync is a no-op** — identical copies are skipped, not rewritten.
4. **`--dry-run` before any real write** when unsure.

## Agent registry

Default roots: `hub=~/.agents/skills` (the cross-agent hub — the path **Codex** reads via native skill discovery), `claude=~/.claude/skills`, `opencode=~/.config/opencode/skills`. **Codex's canonical target is the hub**, not `~/.codex/skills`. An agent only counts as present if its dir (or parent) exists. Add or override roots without editing code — e.g. to also sync a secondary `~/.codex/skills` location some setups use:

```bash
export CROSS_AGENT_SKILL_ROOTS="codex=~/.codex/skills,work=~/work/.agents/skills"
```

## Notes

- This bridges **skills** only. MCP servers and agent definitions live in agent-specific configs and are out of scope for v1 (Claude→Codex MCP re-registration is a separate, config-coupled problem).
- Codex reads `~/.agents/skills/` via native skill discovery; Claude Code uses its plugin marketplace and OpenCode uses `~/.config/opencode/skills/`. This tool doesn't provide that discovery — see CREDITS.
- No third-party dependencies; stdlib Python 3.9+.
