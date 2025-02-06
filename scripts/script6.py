import os
import subprocess
import sys
from dotenv import load_dotenv
import tempfile

# Load the environment variables from .env
load_dotenv()

def main():
    if len(sys.argv) < 6:
        print("Usage: python3 script6.py <fqdn> <country> <state> <locality> <organization> <organizational_unit>")
        sys.exit(1)

    fqdn = sys.argv[1]
    country = sys.argv[2]
    state = sys.argv[3]
    locality = sys.argv[4]
    organization = sys.argv[5]
    organizational_unit = sys.argv[6]

    sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
    base_dir = os.path.expanduser('~/Downloads')
    output_dir = os.path.join(base_dir, f"{sanitized_fqdn}-2025")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    key_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.csr")
    dk_key_file = os.path.join(output_dir, f"DK{sanitized_fqdn}-2025.key")

    # Get the passphrase from the .env file
    passphrase = os.getenv('PASSPHRASE')
    if not passphrase:
        print("Error: PASSPHRASE is not set in the .env file")
        sys.exit(1)

    subject = f"/C={country}/ST={state}/L={locality}/O={organization}/OU={organizational_unit}/CN={fqdn}"

    try:
        # Use a temporary file for passphrase to avoid command-line exposure
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as pass_file:
            pass_file.write(passphrase)
            pass_file.flush()

        # Generate the private key and CSR with passphrase
        subprocess.run(
            ["openssl", "req", "-new", "-newkey", "rsa:2048",
             "-keyout", key_file, "-out", csr_file, "-subj", subject, "-passout", f"file:{pass_file.name}"],
            check=True
        )

        # Generate the decrypted DK file (without passphrase)
        subprocess.run(
            ["openssl", "rsa", "-in", key_file, "-out", dk_key_file, "-passin", f"file:{pass_file.name}"],
            check=True
        )

        # Clean up temporary password file
        os.unlink(pass_file.name)

        # Ensure all files have no trailing blank lines
        for file_path in [key_file, csr_file, dk_key_file]:
            with open(file_path, 'r+', newline='\n') as f:
                content = f.read().rstrip()
                f.seek(0)
                f.write(content)
                f.truncate()

        print(f"All files generated successfully in {output_dir}")

    except subprocess.CalledProcessError as e:
        print(f"Error generating files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
