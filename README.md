# cross-agent-skill-bridge

Author an agent **skill** once, use it in every coding agent you run.

Claude Code, Codex, and Gemini each read "skills" (a `SKILL.md` directory) from a
*different* place — `~/.claude/skills`, `~/.codex/skills`, `~/.gemini/skills` — and
a growing number of agents also natively discover a neutral shared location,
`~/.agents/skills`. So a skill you write for one agent is invisible to the others
until you copy it over. Do that by hand and the copies quietly drift apart.

This is a tiny, dependency-free tool that treats `~/.agents/skills` as a **hub** and
each agent as a **spoke**, and syncs skills between them — **selectively** (you choose
what to share) and **non-destructively** (a copy you've edited is never silently
overwritten).

## Why I built it

I maintain a set of skills across Claude Code and Codex. I wrote one
([`repo-sanitize`](https://github.com/anombyte93/repo-sanitize)) in Claude and wanted
it in Codex too — but I didn't want to blanket-copy *everything*, because some skills
are intentionally agent-specific and some had drifted. I needed to **see** the spread
first, then share just the ones I meant to. That visibility + safe-sync is the whole
tool.

## Install

**One command (any agent):**
```bash
curl -fsSL https://raw.githubusercontent.com/anombyte93/cross-agent-skill-bridge/main/install.sh | bash
```
Clones the repo, symlinks the skill into the neutral `~/.agents/skills` hub, and runs a
smoke test so you can see it working immediately. Idempotent and non-destructive — re-run
to update; it never deletes your skills. Requires `git` and `python3` (3.9+).

**Claude Code (plugin marketplace):**
```
/plugin marketplace add anombyte93/cross-agent-skill-bridge
/plugin install cross-agent-skill-bridge
```

## Use

```bash
cd skills/cross-agent-skill-bridge/scripts

# 1. See what's where, and what's diverged:
python3 skill_bridge.py status

# 2. Preview a share (changes nothing):
python3 skill_bridge.py share --from claude --skill my-skill --dry-run

# 3. Do it (copy to all other present agents):
python3 skill_bridge.py share --from claude --skill my-skill

# Keep a single source-of-truth live everywhere instead of copying:
python3 skill_bridge.py share --from claude --skill my-skill --mode link
```

`status` prints a matrix: rows are skills, columns are agents, cells are content
hashes (`link:…` = symlink, `-` = absent). A `⚠ DIVERGED` row means the copies differ
— decide which is canonical before syncing.

### Safety

- **Non-destructive:** a diverged target is skipped with a warning unless you pass `--force`.
- **Source is read-only:** bridging never deletes or edits the source skill.
- **In-sync = no-op:** identical copies aren't rewritten.
- **`--dry-run`** to preview any operation.

### Extending to other agents

```bash
export CROSS_AGENT_SKILL_ROOTS="opencode=~/.config/opencode/skills,work=~/work/.agents/skills"
```

## Scope

Skills only. MCP servers and agent definitions are agent-specific config and out of
scope for v1.

## Credits

See [CREDITS.md](CREDITS.md). `~/.agents/skills` is the directory Codex reads via native
skill discovery, and the symlink-install pattern is prior art from the agent-skills
ecosystem — notably [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent
(MIT). This tool does not invent that mechanism; it just makes living on both sides of it
painless. (Path scope is agent-specific — Claude Code uses its plugin marketplace, OpenCode
uses `~/.config/opencode/skills/`; see CREDITS.)

## License

[MIT](LICENSE).
