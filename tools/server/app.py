from flask import (
    Flask,
    jsonify,
    send_file,
    render_template_string,
    abort,
    make_response,
)
import json
import os
from pathlib import Path

app = Flask(__name__)

SERVICES_DIR = Path(__file__).parent / "services"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
    <pre>{{ json_content }}</pre>
</body>
</html>
"""

ERROR_TEMPLATE = """
Not found
"""


@app.route("/services")
@app.route("/services/")
def services_root():
    return serve_json_page(".")


@app.route("/services.json")
def services_json():
    return serve_raw_json(".")


@app.route("/services/<path:subpath>")
def services_subpath(subpath):
    subpath = subpath.rstrip("/")
    return serve_json_page(subpath)


@app.route("/services/<path:subpath>.json")
def services_subpath_json(subpath):
    subpath = subpath.rstrip("/")
    return serve_raw_json(subpath)


def serve_json_page(subpath):
    """Serve JSON file as an HTML page"""
    if subpath == ".":
        json_file = SERVICES_DIR / "page.json"
        current_path = "/services"
    else:
        json_file = SERVICES_DIR / subpath / "page.json"
        current_path = f"/services/{subpath}"

    if not json_file.exists():
        return render_template_string(ERROR_TEMPLATE), 404

    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            json_content = json.dumps(data, indent=2)

        return render_template_string(
            HTML_TEMPLATE,
            data=data,
            json_content=json_content,
            current_path=current_path,
        )
    except (json.JSONDecodeError, IOError):
        abort(500)


def serve_raw_json(subpath):
    """Serve raw JSON file for download"""
    if subpath == ".":
        json_file = SERVICES_DIR / "page.json"
        filename = "services.json"
    else:
        json_file = SERVICES_DIR / subpath / "page.json"
        filename = f'{subpath.replace("/", "_")}.json'

    if not json_file.exists():
        return render_template_string(ERROR_TEMPLATE), 404

    try:
        response = make_response(
            send_file(json_file, as_attachment=True, download_name=filename)
        )
        response.headers["Content-Type"] = "application/json"
        return response
    except IOError:
        abort(500)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5432)
