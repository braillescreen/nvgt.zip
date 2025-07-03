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

import requests
from flask import Flask, Response, abort, jsonify, redirect, render_template, request
from flask.typing import ResponseReturnValue

import const

app = Flask(__name__)
if const._DEBUGGING:
	app.logger.setLevel(logging.DEBUG)
	logging.basicConfig(level=logging.DEBUG)


def fetch_nvgt_version() -> str:
	"""Fetch the latest NVGT version string."""
	try:
		response = requests.get(f"{const._BASE_URL}/downloads/latest_version")
		response.raise_for_status()
		return response.text.strip()
	except requests.RequestException as e:
		raise abort(500, description=f"Failed to get NVGT version: {e}")


def fetch_latest_github_release() -> dict:
	"""Fetch the latest GitHub release data."""
	try:
		r = requests.get(f"{const._GITHUB_API}/releases/tags/latest")
		r.raise_for_status()
		return r.json()
	except requests.RequestException as e:
		raise abort(502, description=f"Failed to fetch GitHub release: {e}")


def fetch_github_commits() -> list:
	"""Fetch recent GitHub commits."""
	limit = min(100, max(1, int(request.args.get("limit", 100))))
	try:
		r = requests.get(f"{const._GITHUB_API}/commits?per_page={limit}")
		r.raise_for_status()
		return r.json()
	except requests.RequestException as e:
		raise abort(502, description=f"Failed to fetch GitHub commits: {e}")


def get_extension(platform: str) -> str | None:
	"""Get the file extension for a given platform."""
	return {"android": "apk", "linux": "tar.gz", "mac": "dmg", "windows": "exe"}.get(platform)


@app.route("/")
def home() -> ResponseReturnValue:
	return render_template("index.html")


@app.route("/<platform>")
def download(platform: str) -> ResponseReturnValue:
	"""Redirect to the download for a specific platform."""
	if extension := get_extension(platform):
		version = const.version_cache.get_or_fetch(fetch_nvgt_version)
		return redirect(f"{const._BASE_URL}/downloads/nvgt_{version}.{extension}", code=301)
	return render_template("404.html"), 404


@app.route("/version.json")
def version_json() -> ResponseReturnValue:
	"""Return the latest version as JSON."""
	version = const.version_cache.get_or_fetch(fetch_nvgt_version)
	return jsonify({"version": version})


@app.route("/version")
def version_raw() -> ResponseReturnValue:
	"""Return the latest version as raw text."""
	return const.version_cache.get_or_fetch(fetch_nvgt_version)


@app.route("/dev/<platform>")
def dev_download(platform: str) -> ResponseReturnValue:
	"""Redirect to the development build for a specific platform."""
	if not (extension := get_extension(platform)):
		return render_template("404.html"), 404
	release = const.release_cache.get_or_fetch(fetch_latest_github_release)
	for asset in release.get("assets", []):
		if isinstance(asset, dict) and asset.get("name", "").lower().endswith(f".{extension}"):
			if download_url := asset.get("browser_download_url"):
				return redirect(download_url, code=302)
	return render_template("404.html"), 404


@app.route("/commits.txt")
@app.route("/commits.html")
def commits() -> ResponseReturnValue:
	"""Display recent commits as HTML or plain text."""
	commits_data = const.commits_cache.get_or_fetch(fetch_github_commits)
	if not commits_data:
		raise abort(500, description="Failed to get NVGT commits")
	if request.path.endswith(".txt"):
		lines = []
		for commit in commits_data:
			sha = commit.get("sha", "unknown")[:7]
			author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
			msg = commit.get("commit", {}).get("message", "No message").splitlines()[0]
			lines.append(f"{author} {sha}: {msg}")
		return Response("\n".join(lines), mimetype="text/plain")
	return render_template("commits.html", commits=commits_data)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3105, debug=const._DEBUGGING)
