#!/usr/bin/env python3
"""Kalagana release helper (standard library only).

A small, transparent tool that keeps the version number in one place logically
(it rewrites ``pyproject.toml`` and ``src/kalagana/__init__.py`` together), builds
the distribution, tags the commit, and can create the GitHub release.

Usage
-----
    python scripts/release.py current
    python scripts/release.py bump patch          # 0.1.0 -> 0.1.1
    python scripts/release.py bump minor          # 0.1.1 -> 0.2.0
    python scripts/release.py bump major          # 0.2.0 -> 1.0.0
    python scripts/release.py bump 1.2.3          # set an explicit version
    python scripts/release.py build               # sdist + wheel into dist/
    python scripts/release.py tag                 # annotated tag v<version>
    python scripts/release.py gh-release          # create the GitHub release
    python scripts/release.py release --bump patch  # the whole flow

Safety
------
* ``--dry-run`` prints every command instead of running it.
* ``git push`` only happens when you pass ``--push``; nothing is pushed by
  default.
* The working tree must be clean before ``bump``/``tag``/``release`` unless
  ``--allow-dirty`` is given.

Requires the ``build`` package for ``build``/``release`` (a dev tool, not a
runtime dependency) and the GitHub CLI (``gh``) for ``gh-release``.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
INIT_FILE = REPO_ROOT / "src" / "kalagana" / "__init__.py"
TAG_PREFIX = "v"

_VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>.*)$")


class ReleaseError(RuntimeError):
    """A user-facing failure."""


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------
def parse_version(text: str) -> Tuple[int, int, int, str]:
    m = _VERSION_RE.match(text.strip())
    if not m:
        raise ReleaseError(f"Cannot parse version {text!r}; expected MAJOR.MINOR.PATCH")
    return int(m["major"]), int(m["minor"]), int(m["patch"]), m["suffix"]


def bump_version(current: str, part: str) -> str:
    """Return the next version for ``part`` (major/minor/patch or an explicit version)."""
    major, minor, patch, suffix = parse_version(current)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    # Explicit version (validated).
    parse_version(part)
    return part


def read_pyproject_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not m:
        raise ReleaseError("Could not find `version` in pyproject.toml")
    return m.group(1)


def write_pyproject_version(new: str) -> None:
    text = PYPROJECT.read_text(encoding="utf-8")
    text, n = re.subn(r'^version\s*=\s*"[^"]+"', f'version = "{new}"', text, count=1, flags=re.MULTILINE)
    if n != 1:
        raise ReleaseError("Could not update `version` in pyproject.toml")
    PYPROJECT.write_text(text, encoding="utf-8")


def write_init_version(new: str) -> None:
    text = INIT_FILE.read_text(encoding="utf-8")
    text, n = re.subn(r'^__version__\s*=\s*"[^"]+"', f'__version__ = "{new}"', text, count=1, flags=re.MULTILINE)
    if n != 1:
        raise ReleaseError("Could not update `__version__` in src/kalagana/__init__.py")
    INIT_FILE.write_text(text, encoding="utf-8")


def read_init_version() -> str:
    text = INIT_FILE.read_text(encoding="utf-8")
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if not m:
        raise ReleaseError("Could not find `__version__` in src/kalagana/__init__.py")
    return m.group(1)


# ---------------------------------------------------------------------------
# Command helpers
# ---------------------------------------------------------------------------
def run(cmd: Sequence[str], dry_run: bool = False, check: bool = True) -> int:
    printable = " ".join(cmd)
    if dry_run:
        print(f"[dry-run] {printable}")
        return 0
    print(f"$ {printable}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if check and result.returncode != 0:
        raise ReleaseError(f"Command failed ({result.returncode}): {printable}")
    return result.returncode


def git(*args: str, dry_run: bool = False, check: bool = True, capture: bool = False):
    if capture:
        return subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=check
        ).stdout.strip()
    return run(["git", *args], dry_run=dry_run, check=check)


def is_dirty() -> bool:
    out = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout
    # Ignore untracked build output so a previous `build` does not block tagging.
    for line in out.splitlines():
        path = line[3:].strip()
        if line.startswith("??") and path.split("/")[0] in {"dist", "build", ".venv"}:
            continue
        return True
    return False


def tag_exists(tag: str) -> bool:
    out = subprocess.run(
        ["git", "tag", "--list", tag], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()
    return bool(out)


def ensure_clean(allow_dirty: bool, action: str, dry_run: bool = False) -> None:
    if allow_dirty or dry_run:
        return
    if is_dirty():
        raise ReleaseError(
            f"Working tree is dirty; commit or stash first (or pass --allow-dirty) before {action}."
        )


def ensure_build_tool() -> None:
    try:
        import build  # noqa: F401
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ReleaseError(
            "The 'build' package is required: pip install build"
        ) from exc


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------
def cmd_current(_args: argparse.Namespace) -> int:
    py = read_pyproject_version()
    init = read_init_version()
    flag = "" if py == init else "  (!! mismatched with __init__.py)"
    print(f"{py}{flag}")
    if py != init:
        print(f"  pyproject.toml:        {py}")
        print(f"  kalagana/__init__.py:  {init}")
    return 0


def cmd_bump(args: argparse.Namespace) -> int:
    ensure_clean(args.allow_dirty, "bumping the version", args.dry_run)
    current = read_pyproject_version()
    new = bump_version(current, args.part)
    if new == current:
        print(f"Version already {new}; nothing to do.")
        return 0
    print(f"Bump {current} -> {new}")
    if not args.dry_run:
        write_pyproject_version(new)
        write_init_version(new)
        # Keep the two in sync if one moved.
        assert read_pyproject_version() == read_init_version() == new
    else:
        print("[dry-run] would update pyproject.toml and kalagana/__init__.py")
    if args.commit:
        git("add", "pyproject.toml", "kalagana/__init__.py", dry_run=args.dry_run)
        git("commit", "-m", f"Release {TAG_PREFIX}{new}", dry_run=args.dry_run)
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    ensure_build_tool()
    out = REPO_ROOT / "dist"
    if not args.dry_run:
        shutil.rmtree(out, ignore_errors=True)
    run([sys.executable, "-m", "build", "--outdir", str(out)], dry_run=args.dry_run)
    if not args.dry_run:
        artifacts = sorted(p.name for p in out.glob("*"))
        print("Built:", ", ".join(artifacts) or "(nothing)")
    return 0


def cmd_tag(args: argparse.Namespace) -> int:
    version = read_pyproject_version()
    tag = f"{TAG_PREFIX}{version}"
    if tag_exists(tag):
        raise ReleaseError(f"Tag {tag} already exists.")
    ensure_clean(args.allow_dirty, "tagging", args.dry_run)
    git("tag", "-a", tag, "-m", args.message or f"Kalagana {version}", dry_run=args.dry_run)
    print(f"Tagged {tag}")
    if args.push:
        git("push", "origin", tag, dry_run=args.dry_run)
    else:
        print(f"(not pushed; run: git push origin {tag})")
    return 0


def cmd_gh_release(args: argparse.Namespace) -> int:
    version = read_pyproject_version()
    tag = f"{TAG_PREFIX}{version}"
    if shutil.which("gh") is None:
        raise ReleaseError("GitHub CLI 'gh' not found. Install it, or create the release in the web UI.")
    dist = REPO_ROOT / "dist"
    assets: List[str] = sorted(str(p) for p in dist.glob("*")) if dist.is_dir() else []
    if not assets:
        print("No files in dist/; run `python scripts/release.py build` first.")
    cmd = ["gh", "release", "create", tag, *assets, "--title", f"Kalagana {version}"]
    cmd += ["--notes", args.notes] if args.notes else ["--generate-notes"]
    if args.draft:
        cmd.append("--draft")
    if args.prerelease:
        cmd.append("--prerelease")
    run(cmd, dry_run=args.dry_run)
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    """The whole flow: bump -> build -> tag -> (optionally) push -> GitHub release."""
    if args.bump:
        bump_args = argparse.Namespace(
            part=args.bump, commit=args.commit_bump, dry_run=args.dry_run, allow_dirty=args.allow_dirty
        )
        cmd_bump(bump_args)
    cmd_build(argparse.Namespace(dry_run=args.dry_run))
    tag_args = argparse.Namespace(
        message=None, push=args.push, dry_run=args.dry_run, allow_dirty=args.allow_dirty
    )
    cmd_tag(tag_args)
    if args.gh:
        cmd_gh_release(
            argparse.Namespace(
                notes=args.notes, draft=args.draft, prerelease=args.prerelease, dry_run=args.dry_run
            )
        )
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="release.py", description="Kalagana release helper (stdlib only)."
    )
    p.add_argument("--dry-run", action="store_true", help="print commands instead of running them")
    p.add_argument("--allow-dirty", action="store_true", help="proceed with uncommitted changes")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("current", help="print the current version")
    s.set_defaults(func=cmd_current)

    s = sub.add_parser("bump", help="bump the version (major|minor|patch or an explicit X.Y.Z)")
    s.add_argument("part")
    s.add_argument("--commit", action="store_true", help="git commit the version change")
    s.set_defaults(func=cmd_bump)

    s = sub.add_parser("build", help="build sdist + wheel into dist/")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("tag", help="create the annotated tag v<version>")
    s.add_argument("-m", "--message", help="tag message")
    s.add_argument("--push", action="store_true", help="push the tag to origin")
    s.set_defaults(func=cmd_tag)

    s = sub.add_parser("gh-release", help="create the GitHub release from dist/ artifacts")
    s.add_argument("--notes", help="release notes text (default: --generate-notes)")
    s.add_argument("--draft", action="store_true")
    s.add_argument("--prerelease", action="store_true")
    s.set_defaults(func=cmd_gh_release)

    s = sub.add_parser("release", help="bump -> build -> tag -> (push) -> GitHub release")
    s.add_argument("--bump", choices=["major", "minor", "patch"], help="version bump to apply first")
    s.add_argument("--commit-bump", action="store_true", help="commit the version bump")
    s.add_argument("--push", action="store_true", help="push the tag to origin")
    s.add_argument("--gh", action="store_true", help="also create the GitHub release")
    s.add_argument("--notes", help="release notes text")
    s.add_argument("--draft", action="store_true")
    s.add_argument("--prerelease", action="store_true")
    s.set_defaults(func=cmd_release)

    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
