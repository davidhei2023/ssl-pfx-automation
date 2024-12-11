from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import subprocess
import zipfile
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

        sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
        output_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-2025")

        result = subprocess.run(
            ["python3", "./scripts/script1.py", fqdn],
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


@app.route('/run/script2', methods=['POST'])
def run_script2():
    try:
        data = request.get_json()
        fqdn = data.get('fqdn')
        if not fqdn:
            return jsonify({"error": "FQDN is required"}), 400

        sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
        output_dir = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-wildcard-2025")

        result = subprocess.run(
            ["python3", "./scripts/script2.py", fqdn],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        zip_path = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{sanitized_fqdn}-wildcard-2025.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, output_dir))

        return jsonify({"download_url": f"/download/{sanitized_fqdn}-wildcard-2025.zip"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/run/script3', methods=['POST'])
def run_script3():
    try:
        data = request.get_json()
        cert_content = data.get('certificate')
        key_content = data.get('private_key')
        pfx_name = data.get('pfx_name')

        if not cert_content or not key_content or not pfx_name:
            return jsonify({"error": "All fields are required"}), 400

        pfx_file = os.path.join(app.config['DOWNLOAD_FOLDER'], f"{pfx_name}.pfx")

        # Create temporary files for the certificate and private key
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as cert_file, \
             tempfile.NamedTemporaryFile(delete=False, mode='w') as key_file:
            cert_file.write(cert_content.strip())
            cert_file.flush()
            key_file.write(key_content.strip())
            key_file.flush()

        try:
            # Run OpenSSL to create the PFX file
            result = subprocess.run(
                ["openssl", "pkcs12", "-export", "-out", pfx_file,
                 "-inkey", key_file.name, "-in", cert_file.name, "-password", f"pass:{os.getenv('PFX_PASSWORD', 'Aa1234')}"],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.lower()
            if "unable to load private key" in error_output:
                return jsonify({"error": "The provided private key is invalid or does not match the certificate."}), 400
            elif "no certificate matches private key" in error_output:
                return jsonify({"error": "The certificate and private key do not match."}), 400
            elif "openssl" in error_output:
                return jsonify({"error": "OpenSSL error occurred. Please verify the input."}), 400
            else:
                return jsonify({"error": "An unknown error occurred during PFX creation."}), 400
        finally:
            # Clean up temporary files
            os.unlink(cert_file.name)
            os.unlink(key_file.name)

        return jsonify({"download_url": f"/download/{pfx_name}.pfx"}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


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
        return jsonify({"error": "An unexpected error occurred during file download."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
