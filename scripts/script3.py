import os
import subprocess
import sys

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 script3.py <certificate_file> <private_key_file> <pfx_output_file>")
        sys.exit(1)

    cert_file = sys.argv[1]
    key_file = sys.argv[2]
    pfx_output = sys.argv[3]

    # Validate input files
    if not os.path.exists(cert_file):
        print(f"Error: Certificate file '{cert_file}' does not exist.")
        sys.exit(1)
    if not os.path.exists(key_file):
        print(f"Error: Private key file '{key_file}' does not exist.")
        sys.exit(1)

    try:
        # Run OpenSSL command to generate the PFX file
        subprocess.run(
            ["openssl", "pkcs12", "-export", "-out", pfx_output,
             "-inkey", key_file, "-in", cert_file, "-password", "pass:Aa1234"],
            check=True
        )
        print("PFX file created successfully!")
        print(f"File is located at: {pfx_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to create PFX file. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
