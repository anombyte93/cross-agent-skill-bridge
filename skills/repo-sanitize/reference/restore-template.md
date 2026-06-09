# Archive MANIFEST + Restore Template

Write this `MANIFEST.md` into the archive dir (`~/Archives/<repo>-security-tools-<YYYY-MM-DD>/`) at archive time. It is the rollback contract — without it, the archive is just orphaned files.

## MANIFEST.md template

```markdown
# <repo> security-tooling archive — <YYYY-MM-DD>

Reason: archived offensive-security modules that were tripping the AI content
classifier and blocking agent work on unrelated files. Reversible — see Restore.

## Archived files (origin path → archive path)

| Origin (in repo)            | Archive path                  | Why offensive                         |
|-----------------------------|-------------------------------|---------------------------------------|
| src/security-probes.ts      | src/security-probes.ts        | sends SQLi/XSS/SSRF payloads at target |
| src/shodan-integration.ts   | src/shodan-integration.ts     | Shodan victim discovery               |
| src/cve-lookup.ts           | src/cve-lookup.ts             | CVE DB lookup for exploitation        |
| tests/security-probes.test.ts | tests/security-probes.test.ts | test for archived module             |
| ...                         | ...                           | ...                                   |

## Consumers cleaned (for restore, re-add these)

- src/index.ts — removed MCP tools: rosetta_security, rosetta_report
- src/recon-pipeline.ts — removed Phase 6 security analysis + Shodan Phase 0 call
- CLAUDE.md — removed references to Atlas Fuzzer / 0day-hunt / ffuf / nuclei

## KEPT (false positives — did NOT archive)

- <file> — why it's benign despite trigger words

## Restore procedure

1. Copy each archived file back to its Origin path (preserve src/ + tests/ layout).
2. Re-add the consumer hooks listed above (imports, MCP registrations, pipeline phases).
3. `npx tsc --noEmit && npm test` — confirm green.
4. Delete this archive dir only after restore is verified.
```

## Integrity (optional, recommended for high-risk)

Record hashes so you can prove the restored file matches the archived one:

```bash
find . -type f -exec sha256sum {} \; > MANIFEST.sha256
# restore-time verify:
sha256sum -c MANIFEST.sha256
```
