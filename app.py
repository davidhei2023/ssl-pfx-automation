from flask import Flask, request, jsonify, send_file, render_template
import subprocess
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/run/script1', methods=['POST'])
def run_script1():
    data = request.get_json()
    fqdn = data.get('fqdn')
    if not fqdn:
        return jsonify({"error": "FQDN is required"}), 400

    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{fqdn}-2025")
    key_file = os.path.join(output_dir, f"{fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"{fqdn}-2025.csr")
    os.makedirs(output_dir, exist_ok=True)

    try:
        result = subprocess.run(
            ["python3", "./scripts/script1.py", fqdn],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({
            "key_file": f"/download?file={key_file}",
            "csr_file": f"/download?file={csr_file}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/run/script2', methods=['POST'])
def run_script2():
    data = request.get_json()
    fqdn = data.get('fqdn')
    if not fqdn:
        return jsonify({"error": "FQDN is required"}), 400

    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], f"{fqdn}-wildcard-2025")
    key_file = os.path.join(output_dir, f"wildcard-{fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"wildcard-{fqdn}-2025.csr")
    os.makedirs(output_dir, exist_ok=True)

    try:
        result = subprocess.run(
            ["python3", "./scripts/script2.py", fqdn],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({
            "key_file": f"/download?file={key_file}",
            "csr_file": f"/download?file={csr_file}"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/run/script3', methods=['POST'])
def run_script3():
    data = request.get_json()
    certificate = data.get('certificate')
    private_key = data.get('privateKey')
    pfx_name = data.get('pfxName')

    if not all([certificate, private_key, pfx_name]):
        return jsonify({"error": "Certificate, private key, and PFX name are required"}), 400

    output_dir = app.config['UPLOAD_FOLDER']
    pfx_file = os.path.join(output_dir, f"{pfx_name}.pfx")

    cert_file = os.path.join(output_dir, "temp_cert.pem")
    key_file = os.path.join(output_dir, "temp_key.pem")
    try:
        with open(cert_file, "w") as f:
            f.write(certificate)
        with open(key_file, "w") as f:
            f.write(private_key)

        result = subprocess.run(
            ["python3", "./scripts/script3.py", cert_file, key_file, pfx_name],
            capture_output=True, text=True
        )

        os.remove(cert_file)
        os.remove(key_file)

        if result.returncode != 0:
            return jsonify({"error": result.stderr.strip()}), 500

        return jsonify({"pfx_file": f"/download?file={pfx_file}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download', methods=['GET'])
def download_file():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
