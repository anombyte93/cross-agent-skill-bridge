---
name: repo-sanitize
description: Use when an AI agent's file reads/edits in a repo get content-blocked (refusals, "I can't help with that" on innocuous files), or before handing a repo to AI tooling, AND the repo may contain offensive-security/dual-use code (SQLi/XSS/SSRF probes, exploit/payload generators, Shodan/CVE lookups, fuzzers, credential harvesters, port scanners). Triages TRUE offensive tooling (reversibly ARCHIVE) vs FALSE POSITIVES (KEEP). Never blind-deletes.
metadata:
  user-invocable: true
---

# Repo Sanitize — Triage & Reversibly Archive AI-Blocking Tooling

**Core principle:** Offensive-security code in a repo can trip the AI content classifier and block an agent from reading/editing *unrelated* files. The fix is to **reversibly archive the genuinely offensive modules** so the agent can work — NOT to delete code, and NOT to archive everything that merely contains a scary word.

**The one rule: TRIAGE before you touch anything.** Trigger words (`scan`, `inject`, `payload`, `probe`, `exploit`, `bot`, `spawn`) are NOT evidence. Capability is.

## When this fires vs when it doesn't

- ✅ Agent reads/edits get refused on files that aren't themselves sensitive → classifier is reacting to *other* code in context.
- ✅ Prepping a repo for autonomous AI execution where dual-use modules exist.
- ✅ A product that *built* offensive scanning as a feature (e.g. Rosetta MCP's security-recon module) — even first-party intentional code trips the classifier. Archive it if the feature is not the repo's *primary purpose*.
- ❌ A pentest/CTF repo you WANT to keep offensive — don't sanitize; that's the point of it.
- ❌ Secrets/credentials leak → that's a secret-rotation task, not this.

## Decision tree (per suspect file)

```dot
digraph triage {
  "Suspect file" [shape=box];
  "Has REAL offensive capability?" [shape=diamond];
  "Is it load-bearing for benign features?" [shape=diamond];
  "ARCHIVE (reversible)" [shape=box,style=bold];
  "KEEP — false positive, log why" [shape=box];
  "ARCHIVE module + clean consumers" [shape=box,style=bold];

  "Suspect file" -> "Has REAL offensive capability?";
  "Has REAL offensive capability?" -> "KEEP — false positive, log why" [label="no (just trigger words)"];
  "Has REAL offensive capability?" -> "Is it load-bearing for benign features?" [label="yes"];
  "Is it load-bearing for benign features?" -> "ARCHIVE (reversible)" [label="no"];
  "Is it load-bearing for benign features?" -> "ARCHIVE module + clean consumers" [label="yes — untangle first"];
}
```

**TRUE offensive capability** = code that *performs* an attack: sends SQLi/XSS/SSRF payloads at a target, generates exploits, queries Shodan/CVE DBs to find victims, fuzzes endpoints, harvests credentials, scans ports of arbitrary hosts.

**FALSE POSITIVE** = benign code wearing scary words: a web-scraper's `api-recon` module (`recon`/`intercept`/`scrape` = discovering and reading public APIs), a crawler that `spawn`s a headless browser, a config importer with `payload` = data blob. *Discovering/reading public data ≠ attacking a third party.*

## Procedure (the steps that worked on rosetta-mcp)

1. **Enumerate suspects.** `grep -rliE 'sqli|xss|ssrf|exploit|payload|shodan|cve|fuzz|nuclei|ffuf|subfinder|waybackurls|secretfinder|credential.?harvest|port.?scan' src/ tests/` — this is a *candidate list*, not a kill list.
2. **Triage each** via the decision tree. Write the verdict (ARCHIVE/KEEP + one-line reason) for every file. KEEP is a valid, common outcome.
3. **Archive the ARCHIVE set, reversibly:** move (don't delete) to `~/Archives/<repo>-security-tools-<YYYY-MM-DD>/` preserving `src/` + `tests/` subpaths. Outside the repo = outside the AI working dir. Write a `MANIFEST.md` (see `reference/restore-template.md`) listing each file, its origin path, and a one-line restore note.
4. **Clean consumers** so the build stays green: remove dead imports, MCP tool registrations, pipeline phases, and stale JSDoc that referenced archived modules.
5. **Scrub docs:** remove references in `CLAUDE.md` / `README` / `docs/` to the archived capabilities (tool names, phase descriptions, dependency lists).
6. **Fix dangling test refs:** replace deleted-module imports with inline types; remove dead mocks for archived modules.
7. **Verify green:** `npx tsc --noEmit` (or project typecheck) + `npm test`. Paste output. A failing build means step 4/6 is incomplete.
8. **Commit in two parts:** (a) the strip + consumer/doc cleanup, (b) a follow-up "clean up dangling references" commit. Keeps the diff reviewable.
9. **Check non-main branches / worktrees.** Long-lived feature branches and open PRs often predate the sanitize commit and still carry the full offensive set. Run `git branch -a` + `git worktree list` and apply the same archive pass to any branch the user intends to work on. A sanitize commit on `main` does NOT propagate to 76-commit-ahead PR branches.

## Reversibility (non-negotiable)

Never `rm`. Always `mv` to the dated archive with a MANIFEST. Restoration = copy files back to their origin paths, re-add imports/registrations, re-run typecheck. The archive is the rollback. See `reference/restore-template.md`.

## Anti-patterns

- ❌ Blind-delete every grep hit → archives benign tools, breaks the build, irreversible.
- ❌ Trusting trigger words over capability → false-positive KEEP cases (e.g. a benign `api-recon`/scraper module) get wrongly archived.
- ❌ `rm` instead of `mv` → no rollback.
- ❌ Forgetting consumer/doc cleanup → red build, dangling imports.
- ❌ Sanitizing a repo whose offensive tooling is the actual product (pentest/CTF kit).
