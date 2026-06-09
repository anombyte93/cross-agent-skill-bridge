# Credits & prior art

This tool stands on conventions it did **not** invent. It exists only to make
working across them convenient.

- **The `~/.agents/skills/` location** is the directory Codex reads via **native skill
  discovery** (per Codex's own release notes), and a neutral spot other agents can be
  pointed at. This project treats it as the hub but does not define or own it. Note the
  path is agent-specific: Codex discovers `~/.agents/skills/` natively, **Claude Code**
  installs skills via its plugin marketplace / native `Skill` tool, and **OpenCode** uses
  `~/.config/opencode/skills/`. So `~/.agents/skills` is the shared hub for
  native-discovery agents, not a single universal path every agent reads.

- **[Superpowers](https://github.com/obra/superpowers)** by **Jesse Vincent (obra)**,
  MIT licensed — demonstrates the install pattern of symlinking a `skills/` directory
  into `~/.agents/skills/` for native-discovery agents (notably Codex). The hub-and-spoke
  model here follows that established pattern. If you want a full batteries-included skill
  *suite*, use Superpowers; this tool is just a focused sync/visibility utility.

- **The `SKILL.md` format** (YAML frontmatter + Markdown body) is the Claude Code /
  agent-skills format documented at https://code.claude.com/docs/en/skills.

- This project was generalized from a personal `claude-to-codex-migration` skill into
  a bi-directional, selective, non-destructive bridge.

If you believe attribution is missing or incorrect, please open an issue.
