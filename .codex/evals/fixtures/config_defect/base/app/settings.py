"""Settings loader (evaluation fixture with a seeded configuration defect)."""
import json
from pathlib import Path

DEFAULTS = {"timeout_seconds": 30, "retries": 3}


def load(path="config.json"):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    merged = dict(DEFAULTS)
    merged.update({k: v for k, v in data.items() if k in DEFAULTS})
    return merged
