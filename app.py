"""
	app.py - main Flask app.
	nvgt.zip
	Copyright (c) 2024 BrailleScreen
	
	This software is provided "as-is", without any express or implied warranty. In no event will the authors be held liable for any damages arising from the use of this software.
	
	Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it and redistribute it freely, subject to the following restrictions:
	
		1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software. If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
		2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
		3. This notice may not be removed or altered from any source distribution.
"""

from flask import Flask, redirect, jsonify, render_template
import requests

app = Flask(__name__)
base_url = "https://nvgt.gg"

def get_nvgt_version() -> str:
	try:
		response = requests.get(f"{base_url}/downloads/latest_version")
		response.raise_for_status()
		return response.text
	except requests.exceptions.RequestException as e:
		abort(500, description=f"Failed to get NVGT version: {str(e)}")

def redirect_to(path: str) -> str:
	return redirect(f"{base_url}/{path}", code=301)

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/<platform>")
def download(platform: str) -> str:
	version = get_nvgt_version()
	extension = get_extension(platform)
	if extension:
		return redirect_to(f"downloads/nvgt_{version}.{extension}")
	return render_template("404.html")

def get_extension(platform: str) -> str:
	match platform:
		case "android":
			return "apk"
		case "linux":
			return "tar.gz"
		case "mac":
			return "dmg"
		case "windows":
			return "exe"
		case _:
			return None

@app.route("/version.json")
def return_nvgt_version(as_json = False, version = get_nvgt_version()):
	return jsonify({"version": version}) if as_json else version

@app.route("/version")
def raw_version(): return return_nvgt_version(False)

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=False, port=3105)
