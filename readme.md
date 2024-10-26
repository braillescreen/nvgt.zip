# [NVGT.zip](https://nvgt.zip)
A small website designed to help you download the latest version of the [Nonvisual Gaming Toolkit](https://nvgt.gg).

## Features
* Use `/mac`, `/win`, etc. to download a version for that particular platform (a full list is on the homepage).
* Use `/version` to get the latest NVGT version in plaintext, or `/version.json` to get it returned in JSON format.

## Running the code
This website is a basic Flask app. I run it through Docker, but you can also run it standalone quite easily.
### Docker
```
git clone https://github.com/braillescreen/nvgt.zip.git
cd nvgt.zip
docker compose up -d
```

### Not docker
```
git clone https://github.com/braillescreen/nvgt.zip.git
cd nvgt.zip
pip3 install -r requirements.txt
python3 app.py
```

The server will be listening on port 3105 on all network interfaces.

## Contributing
Contributions are certainly appreciated! If the change is major especially if it involves existing code, please consider opening a discussion or an issue first.

Enjoy!