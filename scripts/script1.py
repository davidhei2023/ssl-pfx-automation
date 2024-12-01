import os
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python script1.py <fqdn>")
        sys.exit(1)

    fqdn = sys.argv[1]
    sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
    base_dir = os.path.expanduser('~/Downloads')
    output_dir = os.path.join(base_dir, f"{sanitized_fqdn}-2025")

    os.makedirs(output_dir, exist_ok=True)

    key_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"{sanitized_fqdn}-2025.csr")
    dk_key_file = os.path.join(output_dir, f"DK{sanitized_fqdn}-2025.key")

    subject = f"/C=IL/ST=Merkaz/L=Petah Tikva/O=Zap Group ltd/OU=IT Department/CN={fqdn}"

    subprocess.run(
        ["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
         "-keyout", key_file, "-out", csr_file, "-subj", subject],
        check=True
    )

    subprocess.run(
        ["openssl", "rsa", "-in", key_file, "-out", dk_key_file],
        check=True
    )

    print("All files generated successfully!")
    print(f"Files are located in the directory: {output_dir}")

if __name__ == "__main__":
    main()
