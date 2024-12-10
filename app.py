from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import subprocess
import zipfile

app = Flask(__name__)
CORS(app)

BASE_DOWNLOAD_DIR = os.path.expanduser('~/Downloads')
app.config['DOWNLOAD_FOLDER'] = BASE_DOWNLOAD_DIR

if not os.path.exists(BASE_DOWNLOAD_DIR):
    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/run/script6', methods=['POST'])
def run_script6():
    try:
        data = request.get_json()
        fqdn = data.get('fqdn')
        country = data.get('country')
        state = data.get('state')
        locality = data.get('locality')
        organization = data.get('organization')
        organizational_unit = data.get('organizational_unit')

        if not all([fqdn, country, state, locality, organization, organizational_unit]):
            return jsonify({"error": "All fields are required"}), 400

        sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
        output_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-2025")

        result = subprocess.run(
            ["python3", "./scripts/script6.py", fqdn, country, state, locality, organization, organizational_unit],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        zip_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-2025.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, output_dir))

        return jsonify({"download_url": f"/download/{sanitized_fqdn}-2025.zip"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    try:
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
