"""
const.py - constints for the app such as URLs for NVGT, supported platforms etc. Along with a time-based cache.
nvgt.zip
Copyright (c) 2024-2025 BrailleScreen

This software is provided "as-is", without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
	1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
	2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
	3. This notice may not be removed or altered from any source distribution.
"""

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

	base_url: str = "https://nvgt.dev"
	dev_url: str = "https://github.com/samtupy/nvgt"
	github_api: str = "https://api.github.com/repos/samtupy/nvgt"
	debugging: bool = False
	version_cache: Cache = field(default_factory=lambda: Cache(ttl=300))
	release_cache: Cache = field(default_factory=lambda: Cache(ttl=900))
	commits_cache: Cache = field(default_factory=lambda: Cache(ttl=300))
