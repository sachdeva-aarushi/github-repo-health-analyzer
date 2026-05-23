import os
import time
import threading
from typing import Any, Dict, Callable, Tuple
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class RepoCache:
    def __init__(self, default_ttl: int = 10800):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._key_locks: Dict[str, threading.Lock] = {}
        self._registry_lock = threading.Lock()

    def _get_key_lock(self, key: str) -> threading.Lock:
        with self._registry_lock:
            if key not in self._key_locks:
                self._key_locks[key] = threading.Lock()
            return self._key_locks[key]

    def get(self, key: str) -> Tuple[bool, Any]:
        """Returns (hit, value)"""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() < item["expires_at"]:
                    return True, item["value"]
                else:
                    # Expired, clean up
                    del self._cache[key]
            return False, None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires_at": time.time() + ttl
            }

    def get_or_fetch(self, key: str, fetch_fn: Callable[[], Any], ttl: int = None, cache_hit_callback: Callable[[], None] = None) -> Any:
        # First quick check without acquiring the execution lock
        hit, val = self.get(key)
        if hit:
            if cache_hit_callback:
                cache_hit_callback()
            return val

        # Acquire the execution lock for this specific key (Request Deduplication)
        key_lock = self._get_key_lock(key)
        with key_lock:
            # Double check under lock
            hit, val = self.get(key)
            if hit:
                if cache_hit_callback:
                    cache_hit_callback()
                return val

            # Fetch the data
            val = fetch_fn()
            self.set(key, val, ttl)
            return val

# Configurable TTL (default 6 hours)
CACHE_TTL = int(os.getenv("CACHE_TTL", "21600"))

# Global cache instance
global_cache = RepoCache(default_ttl=CACHE_TTL)
