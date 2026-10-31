from flask import Flask, abort, send_from_directory
import os

# no built-in static route: only the files listed below are ever served
app = Flask(__name__, static_folder=None)

ROOT = os.path.dirname(os.path.abspath(__file__))

# everything the page links to; anything else in the repo stays private
PUBLIC_FILES = {
    "apple-touch-icon.png",
    "coe-logo.png",
    "favicon.png",
    "favicon.svg",
    "index.html",
    "og-image.png",
    "resume.pdf",
}


@app.route("/")
def index():
    return send_from_directory(ROOT, "index.html")


@app.route("/<path:path>")
def static_files(path):
    if path not in PUBLIC_FILES:
        abort(404)
    return send_from_directory(ROOT, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
