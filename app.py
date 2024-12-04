from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import subprocess
import tempfile
import zipfile

app = Flask(__name__)
CORS(app)

BASE_DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
app.config["DOWNLOAD_FOLDER"] = BASE_DOWNLOAD_DIR

# Ensure the base download directory exists
if not os.path.exists(BASE_DOWNLOAD_DIR):
    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)


@app.route("/")
def homepage():
    return render_template("index.html")


def create_zip(output_dir, fqdn):
    """Create a ZIP file containing all generated files."""
    zip_filename = os.path.join(output_dir, f"{fqdn}-2025.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_dir))
    return zip_filename


@app.route("/run/script1", methods=["POST"])
def run_script1():
    try:
        data = request.get_json()
        fqdn = data.get("fqdn")
        if not fqdn:
            return jsonify({"error": "FQDN is required"}), 400

        sanitized_fqdn = fqdn.translate({ord(c): None for c in r":\/\*?\"<>|"})
        output_dir = os.path.join(app.config["DOWNLOAD_FOLDER"], f"{sanitized_fqdn}-2025")
        os.makedirs(output_dir, exist_ok=True)

        # Run script1.py
        result = subprocess.run(
            ["python3", "./scripts/script1.py", fqdn],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        # Create a ZIP archive
        zip_file = create_zip(output_dir, sanitized_fqdn)

        return jsonify({
            "zip_file": f"/download/{sanitized_fqdn}-2025/{os.path.basename(zip_file)}",
            "message": "Script 1 executed successfully and files are zipped."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/run/script2", methods=["POST"])
def run_script2():
    try:
        data = request.get_json()
        fqdn = data.get("fqdn")
        if not fqdn:
            return jsonify({"error": "FQDN is required"}), 400

        sanitized_fqdn = fqdn.translate({ord(c): None for c in r":\/\*?\"<>|"})
        output_dir = os.path.join(app.config["DOWNLOAD_FOLDER"], f"{sanitized_fqdn}-wildcard-2025")
        os.makedirs(output_dir, exist_ok=True)

        # Run script2.py
        result = subprocess.run(
            ["python3", "./scripts/script2.py", fqdn],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        # Create a ZIP archive
        zip_file = create_zip(output_dir, sanitized_fqdn)

        return jsonify({
            "zip_file": f"/download/{sanitized_fqdn}-wildcard-2025/{os.path.basename(zip_file)}",
            "message": "Script 2 executed successfully and files are zipped."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/run/script3", methods=["POST"])
def run_script3():
    try:
        data = request.get_json()
        cert_content = data.get("cert_content")
        key_content = data.get("key_content")
        pfx_output_name = data.get("pfx_output")

        if not cert_content or not key_content or not pfx_output_name:
            return jsonify({"error": "All fields are required"}), 400

        temp_dir = tempfile.gettempdir()
        cert_file = os.path.join(temp_dir, "cert.pem")
        key_file = os.path.join(temp_dir, "key.pem")
        pfx_output_file = os.path.join(app.config["DOWNLOAD_FOLDER"], f"{pfx_output_name}.pfx")

        with open(cert_file, "w", encoding="utf-8") as cf, open(key_file, "w", encoding="utf-8") as kf:
            cf.write(cert_content.strip())
            kf.write(key_content.strip())

        result = subprocess.run(
            ["openssl", "pkcs12", "-export", "-out", pfx_output_file,
             "-inkey", key_file, "-in", cert_file, "-password", "pass:Aa1234"],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"error": f"OpenSSL error: {result.stderr.strip()}"}), 500

        return jsonify({
            "pfx_file": f"/download/{os.path.basename(pfx_output_file)}",
            "message": "PFX file created successfully."
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<path:filepath>", methods=["GET"])
def download(filepath):
    try:
        directory, filename = os.path.split(filepath)
        full_dir = os.path.join(app.config["DOWNLOAD_FOLDER"], directory)

        if not os.path.exists(os.path.join(full_dir, filename)):
            return jsonify({"error": f"File '{filename}' not found in '{full_dir}'."}), 404

        return send_file(
            os.path.join(full_dir, filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
