"""Offline gates, leakage-free paired prompts, and imported response checks. No API calls."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from common import emit, load_json
from decision import decide
from validate import ROOT

CATEGORIES = {"task", "business", "cost", "risk", "operations"}
DIMENSIONS = {"problem", "selection", "evidence", "tradeoffs", "workflow", "mvp", "evaluation", "explanation"}


def check_response(row, case):
    errors = []
    if not isinstance(row, dict):
        return ["response must be object"]
    if row.get("schema_version") != "1.0" or row.get("case_id") != case["id"]:
        errors.append("schema_version/case_id mismatch")
    if type(row.get("should_trigger")) is not bool or row.get("should_trigger") != case["should_trigger"]:
        errors.append("trigger mismatch")
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())
    if not nonempty(row.get("rationale")):
        errors.append("rationale missing")
    if not case["should_trigger"]:
        return errors
    rec = row.get("recommendation", {})
    if not isinstance(rec, dict):
        return errors + ["recommendation must be object"]
    for key, allowed in {"base": {"manual", "rules", "traditional_algorithm", "retrieval", "llm", "unknown"},
                         "knowledge": {"none", "rag"}, "orchestration": {"direct", "workflow", "single_agent", "multi_agent"},
                         "status": {"candidate", "needs_evidence", "blocked"}}.items():
        if not isinstance(rec.get(key), str) or rec[key] not in allowed:
            errors.append(f"invalid recommendation.{key}")
    if rec.get("knowledge") == "rag" and rec.get("base") != "llm":
        errors.append("RAG requires LLM")
    for key, value in case.get("expected", {}).items():
        if rec.get(key) != value:
            errors.append(f"decision mismatch: {key}")
    for key in ("evidence", "rejected_options", "metrics"):
        if not isinstance(row.get(key), list) or not row[key]:
            errors.append(f"{key} must be nonempty list")
    for item in row.get("evidence", []) if isinstance(row.get("evidence"), list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("role"), str) or item["role"] not in {"user_reported", "verified", "inferred", "simulated", "unknown"} or not all(nonempty(item.get(k)) for k in ("claim", "source", "limitation")):
            errors.append("invalid evidence item")
    for item in row.get("rejected_options", []) if isinstance(row.get("rejected_options"), list) else []:
        if not isinstance(item, dict) or not all(nonempty(item.get(k)) for k in ("option", "reason")):
            errors.append("invalid rejected option")
    metrics = row.get("metrics", [])
    categories = set()
    for item in metrics if isinstance(metrics, list) else []:
        if not isinstance(item, dict):
            errors.append("invalid metric")
            continue
        cat = item.get("category")
        if isinstance(cat, str):
            categories.add(cat)
        if not isinstance(cat, str) or cat not in CATEGORIES or not isinstance(item.get("target_role"), str) or item["target_role"] not in {"observed", "proposed", "simulated", "unknown"} or not all(nonempty(item.get(k)) for k in ("name", "definition", "window", "source", "owner")):
            errors.append("metric fields missing/invalid")
    if categories != CATEGORIES:
        errors.append("five metric categories required")
    for key in ("permissions", "approval", "failure", "fallback", "stop"):
        control = row.get("controls", {})
        if not isinstance(control, dict) or not nonempty(control.get(key)):
            errors.append(f"control missing: {key}")
    mvp = row.get("mvp", {})
    for key in ("p0", "out_of_scope", "user_flow", "acceptance"):
        if not isinstance(mvp, dict) or not isinstance(mvp.get(key), list) or not mvp[key] or not all(nonempty(v) for v in mvp[key]):
            errors.append(f"mvp missing: {key}")
    if not isinstance(row.get("unknowns"), list) or not row["unknowns"] or not all(nonempty(v) for v in row["unknowns"]):
        errors.append("unknowns missing")
    if not nonempty(row.get("experiment")):
        errors.append("experiment missing")
    return errors


def offline(cases):
    rows = []
    for case in cases:
        if not case["should_trigger"]:
            continue  # Trigger routing requires a real model; never simulate it with Python.
        actual = decide(case["decision_input"])
        errors = [key for key, val in case["expected"].items() if actual.get(key) != val]
        rows.append({"id": case["id"], "passed": not errors, "mismatched_fields": errors, "actual": actual})
    return {"mode": "deterministic_gate_regression", "model_evaluation": "not_run", "rows": rows,
            "passed": all(r["passed"] for r in rows), "trigger_cases_not_executed": sum(not c["should_trigger"] for c in cases)}


def prepare(cases, output):
    if output.exists():
        raise ValueError("output already exists; choose a new trial directory")
    # Baseline sees the same task/format, with no skill, oracle, examples or fact flags.
    contract = (ROOT / "references/output-contract.md").read_text(encoding="utf-8")
    instructions = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    refs = "\n\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / "references").glob("*.md")))
    output.mkdir(parents=True)
    manifest = {"status": "prepared_not_run", "skill_sha256": hashlib.sha256((instructions + refs).encode()).hexdigest(),
                "cases_sha256": hashlib.sha256((ROOT / "evals/cases.json").read_bytes()).hexdigest(),
                "arms": ["baseline", "with_skill"], "resource_hashes": {}, "trials": []}
    for case in cases:
        for arm in ("baseline", "with_skill"):
            body = f"Case ID: {case['id']}\n任务：{case['prompt']}\n\n统一输出格式（两组相同）：\n{contract}\n返回单个 JSON；对范围外任务 should_trigger=false。"
            if arm == "with_skill":
                body += "\n\n明确加载 ai-solution-decision 内容：\n" + instructions + "\n" + refs
            path = output / f"{case['id']}.{arm}.txt"
            path.write_text(body, encoding="utf-8")
            manifest["resource_hashes"][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def grade(cases, responses, reviews=None):
    oracle = {c["id"]: c for c in cases}
    seen = set()
    rows = []
    for packet in responses:
        key = (packet.get("case_id"), packet.get("arm"), packet.get("repeat"))
        if key in seen or key[0] not in oracle or key[1] not in {"baseline", "with_skill"} or type(key[2]) is not int or key[2] < 1:
            raise ValueError("duplicate/unknown/invalid trial identity")
        seen.add(key)
        # Missing telemetry is never invented by this importer.
        telemetry = packet.get("telemetry")
        if not isinstance(telemetry, dict) or any(k not in telemetry for k in ("model", "config_hash", "input_tokens", "output_tokens", "latency_ms", "cost", "trace_ref")):
            raise ValueError("telemetry fields required; use null for unavailable observations")
        errors = check_response(packet.get("response"), oracle[key[0]])
        rows.append({"case_id": key[0], "arm": key[1], "repeat": key[2], "passed": not errors,
                     "errors": errors, "telemetry": telemetry})
    manual = []
    review_seen = set()
    for review in reviews or []:
        key = (review.get("case_id"), review.get("arm"), review.get("repeat"))
        if key not in seen or key in review_seen:
            raise ValueError("manual review has missing/duplicate trial")
        review_seen.add(key)
        scores = review.get("scores", {})
        if set(scores) != DIMENSIONS or any(type(v) is not int or v not in (0, 1, 2) for v in scores.values()):
            raise ValueError("eight rubric scores required, each integer 0..2")
        if type(review.get("critical_failure")) is not bool or not review.get("reviewer") or not review.get("evidence_notes"):
            raise ValueError("review identity, evidence notes and critical_failure required")
        passed = not review["critical_failure"] and min(scores.values()) >= 1 and all(scores[k] == 2 for k in ("selection", "evidence", "workflow", "evaluation"))
        manual.append({**review, "passed": passed})
    pairs = sum((cid, "with_skill", repeat) in seen for cid, arm, repeat in seen if arm == "baseline")
    unpaired = [list(k) for k in sorted(seen) if (k[0], "with_skill" if k[1] == "baseline" else "baseline", k[2]) not in seen]
    covered = {r["case_id"] for r in rows}
    missing_cases = sorted(set(oracle) - covered)
    structural = bool(rows) and all(r["passed"] for r in rows)
    return {"mode": "imported_model_output_checks", "rows": rows, "matched_pairs": pairs,
            "unpaired_trials": unpaired, "missing_cases": missing_cases,
            "structure_and_oracle_passed": structural,
            "manual_reviews": manual, "missing_manual_reviews": len(seen - review_seen),
            "promotion": "not_automated: inspect pairing, repeated variance, semantics and security traces",
            "passed": structural and not unpaired and not missing_cases and seen == review_seen and all(r["passed"] for r in manual)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["offline", "prepare", "grade"])
    p.add_argument("--output", type=Path)
    p.add_argument("--responses", type=Path)
    p.add_argument("--reviews", type=Path)
    args = p.parse_args()
    try:
        cases = load_json(ROOT / "evals/cases.json")
        if args.mode == "prepare":
            if args.output is None:
                raise ValueError("--output required")
            report = prepare(cases, args.output)
        elif args.mode == "grade":
            if args.responses is None:
                raise ValueError("--responses required")
            report = grade(cases, load_json(args.responses), load_json(args.reviews) if args.reviews else None)
        else:
            report = offline(cases)
        emit(report)
        return 0 if report.get("passed", True) else 1
    except (ValueError, KeyError, OSError, TypeError) as exc:
        print(f"eval error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
