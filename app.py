from flask import Flask, request, abort, send_file, jsonify
import datetime
import os
import json

app = Flask(__name__)

# =====================
# Base paths
# =====================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "visits.jsonl")

os.makedirs(LOG_DIR, exist_ok=True)

# =====================
# File serving config
# =====================
ALLOWED_EXTENSIONS = {".txt", ".json", ".bin", ".svg"}

def is_safe_path(base, path):
    real_base = os.path.realpath(base)
    real_path = os.path.realpath(path)
    return real_path.startswith(real_base)

# =====================
# File server endpoint
# =====================
@app.route("/files", methods=["GET"])
def files():
    print("==== FILE REQUEST ====")
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

# =====================
# Collector endpoint (MERGED)
# =====================
@app.route("/collect", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def collect():
    headers = dict(request.headers)

    entry = {
        # Time / request line
        "time_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "remote_addr": request.remote_addr,
        "method": request.method,
        "scheme": request.scheme,
        "host": request.host,
        "path": request.full_path,

        # Params
        "query_params": request.args.to_dict(flat=False),

        # Headers (full capture)
        "headers": headers,

        # Explicit auth-related headers
        "authorization": headers.get("Authorization"),
        "proxy_authorization": headers.get("Proxy-Authorization"),
        "x_api_key": headers.get("X-Api-Key"),
        "x_auth_token": headers.get("X-Auth-Token"),

        # Cookies
        "cookies": request.cookies,

        # Proxy / infra signals
        "forwarded_for": headers.get("X-Forwarded-For"),
        "forwarded_proto": headers.get("X-Forwarded-Proto"),
        "forwarded_host": headers.get("X-Forwarded-Host"),

        # Client metadata
        "user_agent": request.user_agent.string,
        "content_type": request.content_type,
        "content_length": request.content_length
    }

    # Raw body capture (size-limited)
    if request.data:
        entry["raw_body"] = request.data[:8192].decode("utf-8", errors="replace")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return jsonify({"status": "ok"}), 200

# =====================
# App entrypoint
# =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
