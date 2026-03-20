import hashlib
from cachetools import TTLCache
from typing import Dict, Any, Optional

# Cache for 1 hour, max 100 items
cache = TTLCache(maxsize=100, ttl=3600)

def get_cached_result(file_content: bytes) -> Optional[Dict[str, Any]]:
    """Retrieve cached simplified report based on file content hash."""
    file_hash = hashlib.sha256(file_content).hexdigest()
    return cache.get(file_hash)

def set_cached_result(file_content: bytes, result: Dict[str, Any]):
    """Cache simplified report result."""
    file_hash = hashlib.sha256(file_content).hexdigest()
    cache[file_hash] = result
