from flask import Flask, send_from_directory, request, jsonify
from search import find_path as search_find_path

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/find-path", methods=["POST"])
def find_path():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "path": None, "message": "Request body must be JSON"}), 400

    start_raw = data.get("start")
    end_raw = data.get("end")
    start = (str(start_raw) if start_raw is not None else "").strip()
    end = (str(end_raw) if end_raw is not None else "").strip()

    if not start or not end:
        return jsonify({"success": False, "path": None, "message": "Both 'start' and 'end' fields are required"}), 400

    if len(start) > 256 or len(end) > 256:
        return jsonify({"success": False, "path": None, "message": "Article titles must be 256 characters or fewer"}), 400

    try:
        result = search_find_path(start, end)
    except Exception:
        return jsonify({"success": False, "path": None, "message": "Internal server error"}), 500

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok"})


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


if __name__ == "__main__":
    app.run(debug=True)
