# Credits & prior art

This tool stands on conventions it did **not** invent. It exists only to make
working across them convenient.

- **The `~/.agents/skills/` neutral cross-agent skill location** is an emerging
  convention that multiple coding agents (Codex and others) discover natively. This
  project treats it as the hub but does not define or own it.

- **[Superpowers](https://github.com/obra/superpowers)** by **Jesse Vincent (obra)**,
  MIT licensed — demonstrates the cross-agent install pattern (symlinking a `skills/`
  directory into `~/.agents/skills/`) for Claude Code, Codex, Gemini, and OpenCode.
  The hub-and-spoke model here follows that established pattern. If you want a full
  batteries-included skill *suite*, use Superpowers; this tool is just a focused
  sync/visibility utility.

- **The `SKILL.md` format** (YAML frontmatter + Markdown body) is the Claude Code /
  agent-skills format documented at https://code.claude.com/docs/en/skills.

- This project was generalized from a personal `claude-to-codex-migration` skill into
  a bi-directional, selective, non-destructive bridge.

If you believe attribution is missing or incorrect, please open an issue.
