import json
import hashlib
import pathlib
from typing import Optional, Tuple

CACHE_PATH = pathlib.Path("data/vendor_cache.json")
CACHE_PATH.parent.mkdir(exist_ok=True)

def _key(description: str) -> str:
    return hashlib.sha256(description.encode()).hexdigest()[:16]

def get(description: str) -> Optional[Tuple[str, str]]:
    if CACHE_PATH.exists():
        data = json.loads(CACHE_PATH.read_text())
        result = data.get(_key(description))
        return tuple(result) if result else None
    return None

def put(description: str, category: str, vendor: str) -> None:
    data = {}
    if CACHE_PATH.exists():
        data = json.loads(CACHE_PATH.read_text())
    data[_key(description)] = (category, vendor)
    CACHE_PATH.write_text(json.dumps(data)) 