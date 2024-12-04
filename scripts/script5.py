import os
import subprocess
import sys

def main():
    if len(sys.argv) < 6:
        print("Usage: python script5.py <fqdn> <country> <state> <locality> <organization> <orgUnit>")
        sys.exit(1)

    fqdn, country, state, locality, organization, org_unit = sys.argv[1:]
    sanitized_fqdn = fqdn.translate({ord(c): None for c in r':\/\*?"<>|'})
    base_dir = os.path.expanduser('~/Downloads') if os.name != 'nt' else os.path.expanduser('~\\Downloads')
    output_dir = os.path.join(base_dir, f"{sanitized_fqdn}-wildcard-2025")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    key_file = os.path.join(output_dir, f"wildcard-{sanitized_fqdn}-2025.key")
    csr_file = os.path.join(output_dir, f"wildcard-{sanitized_fqdn}-2025.csr")
    dk_key_file = os.path.join(output_dir, f"DKwildcard-{sanitized_fqdn}-2025.key")

    # Define the subject for the CSR
    subject = f"/C={country}/ST={state}/L={locality}/O={organization}/OU={org_unit}/CN={fqdn}"

    try:
        # Generate the private key and CSR
        subprocess.run(
            ["openssl", "req", "-new", "-newkey", "rsa:2048", "-nodes",
             "-keyout", key_file, "-out", csr_file, "-subj", subject],
            check=True
        )

        # Generate the DK file (Decrypted Key)
        subprocess.run(
            ["openssl", "rsa", "-in", key_file, "-out", dk_key_file],
            check=True
        )

        print("All files generated successfully!")
        print(f"Files are located in the directory: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to generate files. {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
