import os
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 script2.py <fqdn>")
        sys.exit(1)

    fqdn = sys.argv[1]
    sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
    base_dir = os.path.expanduser('~/Downloads')
    output_dir = os.path.join(base_dir, f"{sanitized_fqdn}-wildcard-2025")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    key_file = os.path.join(output_dir, f"wildcard-{sanitized_fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"wildcard-{sanitized_fqdn}-2025.csr")
    dk_key_file = os.path.join(output_dir, f"DKwildcard-{sanitized_fqdn}-2025.key")

    subject = f"/C=IL/ST=Merkaz/L=Petah Tikva/O=Zap Group ltd/OU=IT/CN={fqdn}"

    try:
        # Generate the private key and CSR
        subprocess.run(
            ["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
             "-keyout", key_file, "-out", csr_file, "-subj", subject],
            check=True
        )

        # Generate the decrypted DK file
        subprocess.run(
            ["openssl", "rsa", "-in", key_file, "-out", dk_key_file],
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

