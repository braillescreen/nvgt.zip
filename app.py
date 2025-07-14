"""
app.py - main Flask app.
nvgt.zip
Copyright (c) 2024-2025 BrailleScreen

This software is provided "as-is", without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.

Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
	1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
	2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
	3. This notice may not be removed or altered from any source distribution.
"""

import logging
from functools import wraps
from typing import Any, Callable

import requests
from flask import Flask, Response, abort, jsonify, redirect, render_template, request
from flask.typing import ResponseReturnValue

from const import PLATFORM_EXTENSIONS, Config

config = Config()
app = Flask(__name__)

if config.debugging:
	app.logger.setLevel(logging.DEBUG)
	logging.basicConfig(level=logging.DEBUG)

session = requests.Session()


def handle_api_error(func: Callable) -> Callable:
	"""Decorator to handle request errors and abort on failure."""

	@wraps(func)
	def wrapper(*args, **kwargs) -> Any:
		try:
			return func(*args, **kwargs)
		except requests.RequestException as e:
			app.logger.error(f"API request failed: {e}")
			abort(502, description=f"Failed to fetch data: {e}")

	return wrapper


@handle_api_error
def fetch_from_api(url: str, params: dict = None) -> Any:
	"""Fetch data from a URL and return the JSON/text response."""
	response = session.get(url, params=params)
	response.raise_for_status()
	return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text.strip()


def fetch_nvgt_version() -> str:
	"""Fetch the latest NVGT version string."""
	return fetch_from_api(f"{config.base_url}/downloads/latest_version")


def fetch_latest_github_release() -> dict:
	"""Fetch the latest GitHub release data."""
	return fetch_from_api(f"{config.github_api}/releases/tags/latest")


def fetch_github_commits() -> list:
	"""Fetch recent GitHub commits."""
	limit = min(100, max(1, int(request.args.get("limit", 100))))
	return fetch_from_api(f"{config.github_api}/commits", params={"per_page": limit})


@app.route("/")
def home() -> ResponseReturnValue:
	return render_template("index.html")


@app.route("/<platform>")
def download(platform: str) -> ResponseReturnValue:
	"""Redirect to the download for a specific platform."""
	if extension := PLATFORM_EXTENSIONS.get(platform):
		version = config.version_cache.get_or_fetch(fetch_nvgt_version)
		return redirect(f"{config.base_url}/downloads/nvgt_{version}.{extension}", code=301)
	return render_template("404.html"), 404


@app.route("/version.json")
def version_json() -> ResponseReturnValue:
	"""Return the latest version as JSON."""
	version = config.version_cache.get_or_fetch(fetch_nvgt_version)
	return jsonify({"version": version})


@app.route("/version")
@app.route("/version.txt")
def version_raw() -> ResponseReturnValue:
	"""Return the latest version as raw text."""
	return config.version_cache.get_or_fetch(fetch_nvgt_version)


@app.route("/dev/<platform>")
def dev_download(platform: str) -> ResponseReturnValue:
	"""Redirect to the development build for a specific platform."""
	if not (extension := PLATFORM_EXTENSIONS.get(platform)):
		return render_template("404.html"), 404
	release = config.release_cache.get_or_fetch(fetch_latest_github_release)
	for asset in release.get("assets", []):
		if isinstance(asset, dict) and asset.get("name", "").lower().endswith(f".{extension}"):
			if download_url := asset.get("browser_download_url"):
				return redirect(download_url, code=302)
	return render_template("404.html"), 404


@app.route("/commits")
@app.route("/commits.txt")
@app.route("/commits.html")
def commits() -> ResponseReturnValue:
	"""Display recent commits as HTML or plain text."""
	commits_data = config.commits_cache.get_or_fetch(fetch_github_commits)
	if not commits_data:
		abort(500, description="Failed to get NVGT commits")
	if request.path.endswith((".txt", "/commits")):
		lines = [
			(
				f"{commit.get('commit', {}).get('author', {}).get('name', 'Unknown')} "
				f"{commit.get('sha', 'unknown')[:7]}: "
				f"{commit.get('commit', {}).get('message', 'No message').splitlines()[0]}"
			)
			for commit in commits_data
		]
		return Response("\n".join(lines), mimetype="text/plain")
	return render_template("commits.html", commits=commits_data)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3105, debug=config.debugging)
