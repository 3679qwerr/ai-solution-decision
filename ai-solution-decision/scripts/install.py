"""Install a new skill directory into a user-selected host skill root; never overwrite."""
import argparse
import shutil
import sys
from pathlib import Path
from validate import ROOT, validate


def install(source, skills_dir):
    source = source.resolve()
    target = skills_dir.resolve() / "ai-solution-decision"
    if target.exists():
        raise ValueError(f"destination exists; inspect/version it before installing: {target}")
    if target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError("source and destination cannot contain each other")
    problems = validate(source)
    if problems:
        raise ValueError("invalid source: " + "; ".join(problems))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(install(ROOT, args.skills_dir))
    except (ValueError, OSError) as exc:
        print(f"install error: {exc}", file=sys.stderr)
        sys.exit(2)
