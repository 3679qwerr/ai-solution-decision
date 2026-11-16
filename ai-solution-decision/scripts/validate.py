"""Offline package integrity checker, intentionally not a behavioral evaluator."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["SKILL.md", "agents/openai.yaml", "README.md", "LICENSE", "ATTRIBUTION.md",
            "references/selection-matrix.md", "references/business-models.md",
            "references/research-protocol.md", "references/output-contract.md",
            "references/output-rubric.md", "references/evaluation.md", "references/workflow-and-controls.md",
            "references/cost-method.md", "licenses/CC-BY-4.0.txt", "licenses/MIT.txt",
            "scripts/cost_model.py", "scripts/decision.py", "scripts/eval_runner.py",
            "scripts/install.py", "evals/cases.json", "evals/PROTOCOL.md", "tests/test_skill.py"]


def validate(root=ROOT):
    errors = [f"missing: {p}" for p in REQUIRED if not (root / p).is_file()]
    if errors:
        return errors
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    front = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not front or not re.search(r"^name: ai-solution-decision$", front[1], re.M):
        errors.append("invalid skill frontmatter/name")
    elif not re.search(r'^description: ".+"$', front[1], re.M):
        errors.append("description missing")
    if root.name != "ai-solution-decision":
        errors.append("directory must match skill name")
    for path in root.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]\n]+\]\(([^)]+)\)", content):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = unquote(target.split("#")[0].strip("<>"))
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f"broken/escaping reference: {path.relative_to(root)} -> {target}")
    for path in root.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        except (ValueError, OSError) as exc:
            errors.append(f"invalid JSON: {path.name}: {exc}")
    cases = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
    if len(cases) < 10 or len({c["id"] for c in cases}) != len(cases):
        errors.append("eval coverage requires >=10 unique cases")
    for name in ("enterprise-marketing", "xiaoman-companion"):
        for item in ("input.md", "output.md", "decision-input.json", "cost-input.json", "cost-output.json"):
            if not (root / "examples" / name / item).is_file():
                errors.append(f"example incomplete: {name}/{item}")
    meta = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if "$ai-solution-decision" not in meta or "allow_implicit_invocation: true" not in meta:
        errors.append("metadata invocation mismatch")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    problems = validate(args.root)
    print(json.dumps({"passed": not problems, "errors": problems}, ensure_ascii=False, indent=2))
    sys.exit(bool(problems))
