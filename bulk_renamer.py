#!/usr/bin/env python3
"""bulk-renamer: safe, dry-run-first bulk file renaming."""
import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

LOG_FILE = Path.home() / ".bulk_renamer_undo.json"


def to_words(s):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    return [w for w in re.split(r"[\s_\-\.]+", s) if w]


def convert_case(stem, mode):
    if mode == "lower":
        return stem.lower()
    if mode == "upper":
        return stem.upper()
    if mode == "title":
        return stem.title()
    if mode == "snake":
        return "_".join(w.lower() for w in to_words(stem))
    if mode == "kebab":
        return "-".join(w.lower() for w in to_words(stem))
    return stem


def collect(root, pattern, recursive):
    root = Path(root)
    if root.is_file():
        return [root]
    it = root.rglob("*") if recursive else root.iterdir()
    files = [p for p in it if p.is_file() and fnmatch.fnmatch(p.name, pattern)]
    return sorted(files, key=lambda p: str(p).lower())


def new_name(path, args, index):
    stem, ext = path.stem, path.suffix
    if args.replace:
        stem = stem.replace(args.replace[0], args.replace[1])
    if args.regex:
        stem = re.sub(args.regex[0], args.regex[1], stem)
    if args.case:
        stem = convert_case(stem, args.case)
    if args.number:
        stem = str(args.start + index).zfill(args.pad)
    stem = f"{args.prefix or ''}{stem}{args.suffix or ''}"
    if args.ext is not None:
        ext = "." + args.ext.lstrip(".") if args.ext else ""
    return stem + ext


def build_plan(args):
    files = collect(args.path, args.glob, args.recursive)
    plan, targets = [], set()
    for i, f in enumerate(files):
        target = f.with_name(new_name(f, args, i))
        if target == f:
            continue
        key = str(target).lower()
        conflict = key in targets or (target.exists() and target != f)
        targets.add(key)
        plan.append((f, target, conflict))
    return plan


def undo():
    if not LOG_FILE.exists():
        print("Nothing to undo.")
        return 1
    moves = json.loads(LOG_FILE.read_text(encoding="utf-8"))
    for new, old in reversed(moves):
        if os.path.exists(new) and not os.path.exists(old):
            os.rename(new, old)
            print(f"{new} -> {old}")
        else:
            print(f"skip: {new}", file=sys.stderr)
    LOG_FILE.unlink()
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="bulk-renamer", description=__doc__)
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--replace", nargs=2, metavar=("OLD", "NEW"))
    p.add_argument("--regex", nargs=2, metavar=("PATTERN", "REPL"))
    p.add_argument("--case", choices=["lower", "upper", "title", "snake", "kebab"])
    p.add_argument("--prefix")
    p.add_argument("--suffix")
    p.add_argument("--ext")
    p.add_argument("--number", action="store_true")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--pad", type=int, default=3)
    p.add_argument("--glob", default="*")
    p.add_argument("-r", "--recursive", action="store_true")
    p.add_argument("--apply", action="store_true", help="actually rename")
    p.add_argument("--undo", action="store_true", help="revert last run")
    args = p.parse_args(argv)

    if args.undo:
        return undo()

    plan = build_plan(args)
    if not plan:
        print("No changes.")
        return 0

    bad = 0
    for src, dst, conflict in plan:
        mark = "CONFLICT" if conflict else "ok"
        bad += conflict
        print(f"[{mark}] {src.name} -> {dst.name}")

    if bad:
        print(f"\n{bad} conflict(s). Aborting.", file=sys.stderr)
        return 1
    if not args.apply:
        print(f"\nDry run: {len(plan)} file(s). Use --apply to rename.")
        return 0

    done = []
    for src, dst, _ in plan:
        os.rename(src, dst)
        done.append([str(dst), str(src)])
    LOG_FILE.write_text(json.dumps(done), encoding="utf-8")
    print(f"\nRenamed {len(done)} file(s). Undo with: bulk-renamer --undo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
