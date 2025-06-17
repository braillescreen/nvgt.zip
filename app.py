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

from flask import Flask, redirect, jsonify, render_template, abort, Response, request
import const, requests, sys, time
import logging

app = Flask(__name__)
if const._DEBUGGING:
	app.logger.setLevel(logging.DEBUG)
	logging.basicConfig(level=logging.DEBUG)

def get_nvgt_version(force_refresh: bool = False) -> str:
	if not force_refresh and const._version and (time.time() - const._time < const._TTL):
		return const._version
	try:
		response = requests.get(f"{const._BASE_URL}/downloads/latest_version")
		response.raise_for_status()
		const._version = response.text.strip()
		const._time = time.time()
		return const._version
	except requests.RequestException as e:
		abort(500, description=f"Failed to get NVGT version: {e}")

def redirect_to(path: str, use_dev: bool = False) -> str:
	return redirect(f"{const._DEV_URL if use_dev else const._BASE_URL}/{path}", code=301)

def get_extension(platform: str) -> str | None:
	extensions = {
		"android": "apk",
		"linux": "tar.gz",
		"mac": "dmg",
		"windows": "exe"
	}
	return extensions.get(platform)

def get_latest_github_release():
	if not const._release or time.time() - const._release_time > const._TTL:
		try:
			r = requests.get(f"{const._GITHUB_API}/releases/tags/latest")
			if r.ok:
				const._release = r.json()
				const._release_time = time.time()
			else:
				abort(502)
		except requests.RequestException as e:
			abort(502, description=f"Failed to fetch GitHub release: {e}")
	else:
		return const._release

def get_github_commits(limit=100):
	limit = min(100, max(1, int(limit)))
	if not const._commits or time.time() - const._commits_time > const._TTL:
		try:
			r = requests.get(f"{const._GITHUB_API}/commits?per_page={limit}")
			if r.ok:
				const._commits = r.json()
				const._commits_time = time.time()
			else:
				abort(502)
		except requests.RequestException as e:
			abort(502, description=f"Failed to fetch GitHub commits: {e}")
	return const._commits[:limit]

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/<platform>")
def download(platform: str) -> str:
	extension = get_extension(platform)
	if extension:
		version = get_nvgt_version()
		return redirect_to(f"downloads/nvgt_{version}.{extension}")
	return render_template("404.html"), 404

@app.route("/version.json")
def version_json() -> str:
	version = get_nvgt_version()
	return jsonify({"version": version})

@app.route("/version")
def version_raw() -> str:
	return get_nvgt_version()

@app.route("/dev/<platform>")
def dev_download(platform: str) -> str:
	extension = get_extension(platform)
	if not extension:
		return render_template("404.html"), 404
	release = get_latest_github_release()
	assets = release.get("assets", [])
	if not assets:
		return render_template("404.html"), 404
	for i, asset in enumerate(assets):
		if not isinstance(asset, dict):
			continue
		name = asset.get("name", "").lower()
		download_url = asset.get("browser_download_url")
		if name.endswith(f".{extension}")and download_url:
			return redirect(download_url, code=302)
	return render_template("404.html"), 404

@app.route("/commits.txt")
@app.route("/commits.html")
def commits() -> str:
	limit = request.args.get("limit", 100)
	commits = get_github_commits(limit)
	if commits:
		if request.path.endswith(".txt"):
			lines = []
			for commit in commits:
				try:
					sha = commit.get("sha", "unknown")[:7]
					author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
					msg = commit.get("commit", {}).get("message", "No message").splitlines()[0]
					lines.append(f"{author} {sha}: {msg}")
				except (KeyError, TypeError, AttributeError):
					continue
			return Response("\n".join(lines), mimetype="text/plain")
		return render_template("commits.html", commits=commits)
	abort(500, description = "Failed to get NVGT commits")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3105, debug=const._DEBUGGING)
