"""Re-run local checks and save real execution evidence. Does not call a model."""
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
SKILL = KIT / "ai-solution-decision"


def main():
    reports = KIT / "reports"
    reports.mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    commands = {
        "package-validation": ["scripts/validate.py"],
        "unit-tests": ["-m", "unittest", "discover", "-s", "tests", "-v"],
        "offline-evals": ["scripts/eval_runner.py", "offline"],
        "marketing-cost": ["scripts/cost_model.py", "--input", "examples/enterprise-marketing/cost-input.json"],
        "xiaoman-cost": ["scripts/cost_model.py", "--input", "examples/xiaoman-companion/cost-input.json"],
        "marketing-decision": ["scripts/decision.py", "--input", "examples/enterprise-marketing/decision-input.json"],
    }
    results = []
    for name, args in commands.items():
        result = subprocess.run([sys.executable, *args], cwd=SKILL, env=env, capture_output=True, text=True, encoding="utf-8")
        log = result.stdout + result.stderr
        (reports / f"{name}.log").write_text(log, encoding="utf-8")
        results.append({"name": name, "command": ["python", *args], "exit_code": result.returncode,
                        "log": f"{name}.log", "log_sha256": hashlib.sha256(log.encode()).hexdigest()})
    suite = (reports / "unit-tests.log").read_text(encoding="utf-8")
    count = re.search(r"Ran (\d+) tests", suite)
    report = {"schema_version": "1.0", "run_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              "timezone": "Asia/Hong_Kong", "python": platform.python_version(), "platform": platform.platform(),
              "test_count": int(count[1]) if count else None, "checks": results,
              "all_passed": all(r["exit_code"] == 0 for r in results),
              "model_ab": "not_run", "real_business_effects": "unknown", "independent_acceptance": "not_performed"}
    (reports / "verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
