import json
from typing import Dict, Any

def write_json(d: Dict[str, Any], path: str) -> None:
    with open(path, "w") as f:
        json.dump(d, f, indent=2)
