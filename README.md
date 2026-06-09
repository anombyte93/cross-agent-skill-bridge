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

It's a Claude Code plugin, and the same `SKILL.md` works for any agent that discovers
`~/.agents/skills`.

**Claude Code (plugin):**
```
/plugin marketplace add anombyte93/cross-agent-skill-bridge
/plugin install cross-agent-skill-bridge
```

**Any agent (manual):** clone and symlink the skill into the neutral hub:
```bash
git clone https://github.com/anombyte93/cross-agent-skill-bridge.git
mkdir -p ~/.agents/skills
ln -s "$(pwd)/cross-agent-skill-bridge/skills/cross-agent-skill-bridge" ~/.agents/skills/cross-agent-skill-bridge
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

See [CREDITS.md](CREDITS.md). The `~/.agents/skills` cross-agent convention and the
symlink-install pattern are prior art from the broader agent-skills ecosystem,
notably [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent (MIT) —
this tool does not invent the standard, it just makes living on both sides of it
painless.

## License

[MIT](LICENSE).
