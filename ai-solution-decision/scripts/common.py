"""Standard-library JSON helpers. No network, credentials or implicit prices."""
import json
import math
from pathlib import Path


def load_json(path):
    def reject(value):
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), parse_constant=reject)


def number(value, name, low=0, high=None, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: finite number required")
    if value < low or (high is not None and value > high) or (integer and int(value) != value):
        raise ValueError(f"{name}: value outside allowed range")
    return value


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
