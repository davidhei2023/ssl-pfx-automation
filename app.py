from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

# Directory to store generated files
BASE_DOWNLOAD_DIR = os.path.expanduser('~/Downloads')
app.config['DOWNLOAD_FOLDER'] = BASE_DOWNLOAD_DIR

# Ensure the base download directory exists
if not os.path.exists(BASE_DOWNLOAD_DIR):
    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/run/script1', methods=['POST'])
def run_script1():
    try:
        data = request.get_json()
        fqdn = data.get('fqdn')
        if not fqdn:
            return jsonify({"error": "FQDN is required"}), 400

        # Sanitize FQDN
        sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
        output_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-2025")
        os.makedirs(output_dir, exist_ok=True)

        # Run script1.py to generate the files
        result = subprocess.run(
            ["python3", "./scripts/script1.py", fqdn],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        # Check for the expected output files
        key_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.key")
        csr_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.csr")
        dk_file = os.path.join(output_dir, f"DK{sanitized_fqdn}-2025.key")

        # Verify all files exist
        missing_files = [
            file for file in [key_file, csr_file, dk_file] if not os.path.exists(file)
        ]
        if missing_files:
            return jsonify({"error": f"Missing files: {', '.join(missing_files)}"}), 500

        return jsonify({
            "key_file": f"/download/{sanitized_fqdn}-2025/{sanitized_fqdn}-2025.key",
            "csr_file": f"/download/{sanitized_fqdn}-2025/{sanitized_fqdn}-2025.csr",
            "dk_file": f"/download/{sanitized_fqdn}-2025/DK{sanitized_fqdn}-2025.key"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<path:filepath>', methods=['GET'])
def download(filepath):
    try:
        directory, filename = os.path.split(filepath)
        full_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], directory)

        # Ensure file exists before serving
        if not os.path.exists(os.path.join(full_dir, filename)):
            return jsonify({"error": f"File '{filename}' not found in '{full_dir}'."}), 404

        return send_file(
            os.path.join(full_dir, filename),
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
