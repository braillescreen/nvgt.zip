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
import consts, requests, sys, time

app = Flask(__name__)

def get_nvgt_version(force_refresh: bool = False) -> str:
	if not force_refresh and consts._version and (time.time() - consts._time < consts._TTL):
		return consts._version
	try:
		response = requests.get(f"{consts.BASE_URL}/downloads/latest_version")
		response.raise_for_status()
		consts._version = response.text.strip()
		consts._time = time.time()
		return consts._version
	except requests.RequestException as e:
		abort(500, description=f"Failed to get NVGT version: {e}")

def redirect_to(path: str, use_dev: bool = False) -> str:
	return redirect(f"{consts.DEV_URL if use_dev else consts.BASE_URL}/{path}", code=301)

def get_extension(platform: str) -> str | None:
	extensions = {
		"android": "apk",
		"linux": "tar.gz",
		"mac": "dmg",
		"windows": "exe"
	}
	return extensions.get(platform)

def get_latest_github_release():
	if not consts._release or time.time() - consts._release_time > consts._TTL:
		r = requests.get(f"{consts.GITHUB_API}/releases/latest")
		if r.ok:
			consts._release = r.json()
			consts._release_time = time.time()
		else:
			abort(502)
	return consts._release

def get_github_commits(limit=100):
	limit = min(100, max(1, int(limit)))
	if not consts._commits or time.time() - consts._commits_time > consts._TTL:
		r = requests.get(f"{consts.GITHUB_API}/commits?per_page={limit}")
		if r.ok:
			consts._commits = r.json()
			consts._commits_time = time.time()
		else:
			abort(502)
	return consts._commits[:limit]

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
	for asset in release.get("assets", []):
		name = asset.get("name", "").lower()
		if name.endswith(f".{extension}") and platform in name:
			return redirect(asset.get("browser_download_url"), code=302)
	return render_template("404.html"), 404

@app.route("/commits.txt")
@app.route("/commits.html")
def commits() -> str:
	limit = request.args.get("limit", 100)
	commits = get_github_commits(limit)
	if request.path.endswith(".txt"):
		lines = []
		for commit in commits:
			sha = commit["sha"][:7]
			author = commit["commit"]["author"]["name"]
			msg = commit["commit"]["message"].splitlines()[0]
			lines.append(f"{author} {sha}: {msg}")
		return Response("\n".join(lines), mimetype="text/plain")
	else:
		html = [f'<html><body><h1>Recent {len(commits)} Commits</h1><ul>']
		for commit in commits:
			sha = commit["sha"][:7]
			msg = commit["commit"]["message"]
			author = commit["commit"]["author"]["name"]
			date = commit["commit"]["author"]["date"]
			html.append(f"<li>{sha}<p>{author} on {date}: {msg}</p></li>")
		html.append("</ul></body></html>")
		return Response("".join(html), mimetype="text/html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3105, debug=False)
