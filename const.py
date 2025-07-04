import time
from dataclasses import dataclass, field
from typing import Any, Callable

PLATFORM_EXTENSIONS: dict[str, str] = {
	"android": "apk",
	"linux": "tar.gz",
	"mac": "dmg",
	"windows": "exe",
}


@dataclass
class Cache:
	"""A simple time-based cache."""

	data: Any = None
	timestamp: float = 0.0
	ttl: int = 300

	def get_or_fetch(self, fetch_func: Callable[[], Any]) -> Any:
		"""Get data from cache or fetch if invalid."""
		if self.data is None or (time.time() - self.timestamp > self.ttl):
			self.data = fetch_func()
			self.timestamp = time.time()
		return self.data


@dataclass
class Config:
	"""Represents the application configuration."""

	base_url: str = "https://nvgt.gg"
	dev_url: str = "https://github.com/samtupy/nvgt"
	github_api: str = "https://api.github.com/repos/samtupy/nvgt"
	debugging: bool = False
	version_cache: Cache = field(default_factory=lambda: Cache(ttl=300))
	release_cache: Cache = field(default_factory=lambda: Cache(ttl=900))
	commits_cache: Cache = field(default_factory=lambda: Cache(ttl=900))
