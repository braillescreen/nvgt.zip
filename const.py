import time
from dataclasses import dataclass, field
from typing import Any, Callable

_BASE_URL = "https://nvgt.gg"
_DEV_URL = "https://github.com/samtupy/nvgt"
_GITHUB_API = "https://api.github.com/repos/samtupy/nvgt"
_DEBUGGING = False
_TTL = 300


@dataclass
class Cache:
	"""A simple time-based cache."""

	data: Any = None
	timestamp: float = 0.0
	ttl: int = _TTL

	def is_valid(self) -> bool:
		"""Check if the cache is still valid."""
		return self.data is not None and (time.time() - self.timestamp < self.ttl)

	def get_or_fetch(self, fetch_func: Callable[[], Any]) -> Any:
		"""Get data from cache or fetch if invalid."""
		if not self.is_valid():
			self.data = fetch_func()
			self.timestamp = time.time()
		return self.data


version_cache = Cache()
release_cache = Cache()
commits_cache = Cache()
