import os
import subprocess
import sys
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 script1.py <fqdn>")
        sys.exit(1)

    fqdn = sys.argv[1]
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

    subject = f"/C=IL/ST=Merkaz/L=Petah Tikva/O=Zap Group ltd/OU=IT Department/CN={fqdn}"

    try:
        # Generate the private key and CSR with passphrase
        subprocess.run(
            ["openssl", "req", "-new", "-newkey", "rsa:2048",
             "-keyout", key_file, "-out", csr_file, "-subj", subject, "-passout", f"pass:{passphrase}"],
            check=True
        )

        # Generate the decrypted DK file (without passphrase)
        subprocess.run(
            ["openssl", "rsa", "-in", key_file, "-out", dk_key_file, "-passin", f"pass:{passphrase}"],
            check=True
        )

        # Ensure all files have no trailing blank line
        for file_path in [key_file, csr_file, dk_key_file]:
            with open(file_path, 'r+', newline='\n') as f:
                content = f.read().rstrip()  # Remove trailing whitespace/newlines
                f.seek(0)
                f.write(content)
                f.truncate()  # Remove anything beyond the new end of the file

        print("All files generated successfully!")
        print(f"Files are located in the directory: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate files. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
