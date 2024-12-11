import os
import subprocess
import sys
import tempfile


def main():
    if len(sys.argv) < 4:
        print("Usage: python3 script3.py <certificate_content> <private_key_content> <pfx_output_name>")
        sys.exit(1)

    cert_content = sys.argv[1]
    key_content = sys.argv[2]
    pfx_output = sys.argv[3]
    temp_dir = tempfile.gettempdir()
    cert_file = os.path.join(temp_dir, "cert.pem")
    key_file = os.path.join(temp_dir, "key.pem")
    pfx_file = os.path.join(os.path.expanduser("~/Downloads"), f"{pfx_output}.pfx")

    with open(cert_file, "w") as cf, open(key_file, "w") as kf:
        cf.write(cert_content.strip())
        kf.write(key_content.strip())

    try:
        subprocess.run(
            ["openssl", "pkcs12", "-export", "-out", pfx_file,
             "-inkey", key_file, "-in", cert_file, "-password", "pass:Aa1234"],
            check=True, capture_output=True, text=True
        )
        print(f"Successfully created {pfx_file}")
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.lower()
        if "unable to load private key" in error_output:
            print("Error: The provided private key is invalid or does not match the certificate.")
        elif "no certificate matches private key" in error_output:
            print("Error: The certificate and private key do not match.")
        elif "openssl" in error_output:
            print("Error: OpenSSL error occurred. Please verify the input.")
        else:
            print("Error: An unknown error occurred during PFX creation.")
        sys.exit(1)
    finally:
        os.remove(cert_file)
        os.remove(key_file)


if __name__ == "__main__":
    main()
