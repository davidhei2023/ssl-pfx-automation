import os
import subprocess
import sys

def convert_to_pfx(cert_content, key_content, output_pfx_name):
    # Temporary files for OpenSSL
    cert_file = "/tmp/temp_cert.pem"
    key_file = "/tmp/temp_key.pem"
    output_pfx_file = f"/tmp/{output_pfx_name}.pfx"

    try:
        # Write certificate and key content to temporary files
        with open(cert_file, "w") as f:
            f.write(cert_content)
        with open(key_file, "w") as f:
            f.write(key_content)

        # Convert to PFX
        subprocess.run(
            ["openssl", "pkcs12", "-export", "-out", output_pfx_file,
             "-inkey", key_file, "-in", cert_file,
             "-password", "pass:Aa1234"],
            check=True
        )

        print(f"PFX file created successfully!")
        print(f"PFX file: {output_pfx_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during PFX conversion: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Cleanup temporary files
        if os.path.exists(cert_file):
            os.remove(cert_file)
        if os.path.exists(key_file):
            os.remove(key_file)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 script3.py <CERT_CONTENT> <KEY_CONTENT> <OUTPUT_PFX_NAME>", file=sys.stderr)
        sys.exit(1)
    cert_content = sys.argv[1]
    key_content = sys.argv[2]
    output_pfx_name = sys.argv[3]
    convert_to_pfx(cert_content, key_content, output_pfx_name)
