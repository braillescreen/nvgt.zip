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

from flask import Flask, redirect, jsonify, render_template, abort
import requests
import time

app = Flask(__name__)

BASE_URL = "https://nvgt.gg"
DEV_URL = "https://github.com/samtupy/nvgt"

_cached_version = None
_cached_time = 0
CACHE_TTL_SECONDS = 300

def get_nvgt_version(force_refresh: bool = False) -> str:
	global _cached_version, _cached_time
	if not force_refresh and _cached_version and (time.time() - _cached_time < CACHE_TTL_SECONDS):
		return _cached_version
	try:
		response = requests.get(f"{BASE_URL}/downloads/latest_version")
		response.raise_for_status()
		_cached_version = response.text.strip()
		_cached_time = time.time()
		return _cached_version
	except requests.RequestException as e:
		abort(500, description=f"Failed to get NVGT version: {e}")

def redirect_to(path: str, use_dev: bool = False) -> str:
	return redirect(f"{DEV_URL if use_dev else BASE_URL}/{path}", code=301)

def get_extension(platform: str) -> str | None:
	extensions = {
		"android": "apk",
		"linux": "tar.gz",
		"mac": "dmg",
		"windows": "exe"
	}
	return extensions.get(platform)

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

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=3105, debug=False)
