import os
import subprocess
import sys

def generate_wildcard_certificate(fqdn):
    # Sanitize FQDN
    sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})

    # Define file paths
    output_folder = f"/tmp/{sanitized_fqdn}-wildcard-2025"
    key_file = f"{output_folder}/wildcard-{sanitized_fqdn}-2025.key"
    csr_file = f"{output_folder}/wildcard-{sanitized_fqdn}-2025.csr"
    dk_key_file = f"{output_folder}/DKwildcard-{sanitized_fqdn}-2025.key"

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Define the subject for the CSR
    subject = f"/C=IL/ST=Merkaz/L=Petah Tikva/O=Zap Group ltd/OU=IT/CN={fqdn}"

    try:
        # Generate private key and CSR
        subprocess.run(
            ["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
             "-keyout", key_file, "-out", csr_file, "-subj", subject],
            check=True
        )

        # Generate decrypted key
        subprocess.run(
            ["openssl", "rsa", "-in", key_file, "-out", dk_key_file],
            check=True
        )

        print(f"All files generated successfully!")
        print(f"Files are located in the directory: {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error during OpenSSL operations: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script2.py <FQDN>", file=sys.stderr)
        sys.exit(1)
    fqdn = sys.argv[1]
    generate_wildcard_certificate(fqdn)
