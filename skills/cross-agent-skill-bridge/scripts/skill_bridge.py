#!/usr/bin/env python3
"""cross-agent-skill-bridge — share agent skills (SKILL.md dirs) between coding
agents that read from different skill directories.

Hub-and-spoke model: ~/.agents/skills is the neutral cross-agent hub; each agent
(Claude, Codex, Gemini, ...) is a spoke. Sync any direction, selectively, and
NON-DESTRUCTIVELY (diverged copies are never silently clobbered).

stdlib only. No deletion of source. See README for the full model and credits.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

HOME = Path.home()

# Known agent skill roots. An agent is "present" only if its root OR parent exists.
# Override/extend with CROSS_AGENT_SKILL_ROOTS="name=path,name=path".
DEFAULT_ROOTS: dict[str, Path] = {
    "hub": HOME / ".agents" / "skills",      # neutral cross-agent location
    "claude": HOME / ".claude" / "skills",
    "codex": HOME / ".codex" / "skills",
    "gemini": HOME / ".gemini" / "skills",
}


def agent_roots() -> dict[str, Path]:
    roots = dict(DEFAULT_ROOTS)
    extra = os.environ.get("CROSS_AGENT_SKILL_ROOTS", "").strip()
    for pair in filter(None, (p.strip() for p in extra.split(","))):
        name, _, path = pair.partition("=")
        if name and path:
            roots[name.strip()] = Path(path.strip()).expanduser()
    return roots


def present_agents(roots: dict[str, Path]) -> dict[str, Path]:
    # Present if the skills dir exists, or its parent config dir does (so we can create it).
    return {n: p for n, p in roots.items() if p.exists() or p.parent.exists()}


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def list_skills(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {c.name for c in root.iterdir() if is_skill_dir(c)}


def digest(path: Path) -> str:
    """Content hash of a skill dir: sorted relative paths + file bytes.
    Symlinks are resolved to their target content so link==copy compare equal."""
    if not path.exists():
        return ""
    h = hashlib.sha256()
    real = path.resolve()
    for f in sorted(p for p in real.rglob("*") if p.is_file()):
        rel = f.relative_to(real).as_posix()
        h.update(rel.encode())
        h.update(b"\0")
        h.update(f.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def cmd_status(roots: dict[str, Path], _args) -> int:
    agents = present_agents(roots)
    names = sorted(set().union(*(list_skills(p) for p in agents.values())) or set())
    if not names:
        print("No skills found in any present agent dir.")
        return 0

    order = list(agents.keys())
    width = max(len(n) for n in names)
    header = "skill".ljust(width) + "  " + "  ".join(a[:8].ljust(8) for a in order)
    print(header)
    print("-" * len(header))
    for name in names:
        digs = {a: digest(agents[a] / name) for a in order}
        present = [d for d in digs.values() if d]
        diverged = len(set(present)) > 1
        cells = []
        for a in order:
            d = digs[a]
            if not d:
                cells.append("-".ljust(8))
            elif (agents[a] / name).is_symlink():
                cells.append(("link:" + d[:3]).ljust(8))
            else:
                cells.append(d[:8].ljust(8))
        flag = "  ⚠ DIVERGED" if diverged else ""
        print(name.ljust(width) + "  " + "  ".join(cells) + flag)
    print("\nlegend: <hash>=copy  link:<hash>=symlink  -=absent  ⚠=copies differ")
    return 0


def copy_tree(src: Path, dst: Path) -> None:
    if dst.is_symlink() or dst.exists():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.copytree(src.resolve(), dst)


def link_tree(src: Path, dst: Path) -> None:
    if dst.is_symlink() or dst.exists():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    dst.symlink_to(src.resolve(), target_is_directory=True)


def cmd_share(roots: dict[str, Path], args) -> int:
    agents = present_agents(roots)
    if args.source not in agents:
        sys.exit(f"Source agent '{args.source}' not present. Known: {', '.join(agents)}")
    src_root = agents[args.source]

    targets = args.to or [a for a in agents if a != args.source]
    for t in targets:
        if t not in agents:
            sys.exit(f"Target agent '{t}' not present. Known: {', '.join(agents)}")

    if args.all:
        skills = sorted(list_skills(src_root))
    else:
        skills = args.skill
    if not skills:
        sys.exit("Nothing to share: pass --skill NAME (repeatable) or --all.")

    changed = skipped = 0
    for name in skills:
        src = src_root / name
        if not is_skill_dir(src):
            print(f"skip  {name}: not a skill dir in '{args.source}'")
            skipped += 1
            continue
        src_dig = digest(src)
        for t in targets:
            dst = agents[t] / name
            dst_dig = digest(dst)
            if dst_dig == src_dig and dst_dig:
                print(f"ok    {name} -> {t}: already in sync")
                skipped += 1
                continue
            if dst_dig and dst_dig != src_dig and not args.force:
                print(f"WARN  {name} -> {t}: target DIVERGED ({dst_dig} != {src_dig}); "
                      f"use --force to overwrite")
                skipped += 1
                continue
            action = "link" if args.mode == "link" else "copy"
            if args.dry_run:
                verb = "would overwrite" if dst_dig else "would create"
                print(f"DRY   {name} -> {t}: {verb} ({action})")
                continue
            agents[t].mkdir(parents=True, exist_ok=True)
            (link_tree if args.mode == "link" else copy_tree)(src, dst)
            print(f"{action}  {name} -> {t}: {'overwrote' if dst_dig else 'created'}")
            changed += 1
    print(f"\ndone: {changed} written, {skipped} skipped"
          + (" (dry-run)" if args.dry_run else ""))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="skill_bridge",
                                description="Share agent skills between coding agents.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("status", help="Show presence/divergence matrix across agents.")
    sp.set_defaults(fn=cmd_status)

    sh = sub.add_parser("share", help="Share named skill(s) from one agent to others.")
    sh.add_argument("--from", dest="source", required=True, help="Source agent name.")
    sh.add_argument("--to", action="append", default=[], help="Target agent (repeatable). Default: all others.")
    sh.add_argument("--skill", action="append", default=[], help="Skill name (repeatable).")
    sh.add_argument("--all", action="store_true", help="Share every skill in the source agent.")
    sh.add_argument("--mode", choices=["copy", "link"], default="copy",
                    help="copy (default) or symlink for live sync.")
    sh.add_argument("--force", action="store_true", help="Overwrite targets that diverged.")
    sh.add_argument("--dry-run", action="store_true", help="Show what would happen, change nothing.")
    sh.set_defaults(fn=cmd_share)

    args = p.parse_args()
    return args.fn(agent_roots(), args)


if __name__ == "__main__":
    sys.exit(main())
