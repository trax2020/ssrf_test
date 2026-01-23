from flask import Flask, request, abort, send_file
import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")

ALLOWED_EXTENSIONS = {".txt", ".json", ".bin", ".svg"}

def is_safe_path(base, path):
    real_base = os.path.realpath(base)
    real_path = os.path.realpath(path)
    return real_path.startswith(real_base)

@app.route("/files", methods=["GET"])
def files():
    print("==== REQUEST ====")
    print("Time:", datetime.datetime.utcnow())
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("Args:", request.args)

    filename = request.args.get("name")
    if not filename:
        abort(400)

    if filename.startswith("."):
        abort(403)

    _, ext = os.path.splitext(filename)
    if ext not in ALLOWED_EXTENSIONS:
        abort(403)

    file_path = os.path.join(FILES_DIR, filename)

    if not is_safe_path(FILES_DIR, file_path):
        abort(403)

    if not os.path.isfile(file_path):
        abort(404)

    return send_file(file_path, as_attachment=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
