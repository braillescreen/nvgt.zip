# [NVGT.zip](https://nvgt.zip)
A small website designed to help you download the latest version of the [Nonvisual Gaming Toolkit](https://nvgt.dev).

## Features
* Use `/mac`, `/windows`, etc. to download a version for that particular platform (a full list is on the homepage).
* Use `/version` to get the latest NVGT version in plaintext, or `/version.json` to get it returned in JSON format.
* Use `/commits.html` or `/commits.txt` to get the 100 most recent commits to NVGT displayed in that format.

## Running the code
This website backend is a basic Flask app. I run it through Docker, but you can run it standalone quite easily:

Start by cloning the code:
```
git clone https://github.com/braillescreen/nvgt.zip.git
cd nvgt.zip
```

### Running with Docker
```
docker compose up -d
```

#### My one-line restart command
```
cd nvgt.zip; docker compose down; git pull; docker compose up -d
```

### Running standalone using uv
We use [Uv](https://docs.astral.sh/uv/getting-started/installation) for our package manager, as it creates a clean virtual environment.

Assuming you have this repository cloned, simply run `git pull` to update it to the latest commit and run:
```
pip3 install uv
uv run app.py
```

The server is configured to listen on port 3105 on all network interfaces.

## Contributing
Contributions are certainly appreciated! If the change is major especially if it involves existing code, please consider opening a discussion or an issue first. Here are some general guidelines:

### Installing development requirements
We use a formatter, linter, etc. You can install them into a virtual environment with:
```
uv sync --dev
```

It would also be helpful to install our pre-commit hooks using `pre-commit install`.
