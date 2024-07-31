import os
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID
from cryptography import x509
import datetime
import zipfile

current_directory = os.path.dirname(os.path.abspath(__file__))
CERTIFICATES_PATH = os.path.join(current_directory, 'Certificates')

def generate_certificate(apparatus_id):
    # Store a backup of all generated certificates
    #cert_folder = os.path.join(CERTIFICATES_PATH, f"Apparatus_{apparatus_id}_"+str(time.time()))
    cert_folder = os.path.join(CERTIFICATES_PATH, f"Apparatus_{apparatus_id}")
    if not os.path.exists(cert_folder):
        os.makedirs(cert_folder)

    key_path = os.path.join(cert_folder, "stub.key")
    crt_path = os.path.join(cert_folder, "stub.pem")

    ca_key_path = os.path.join(CERTIFICATES_PATH, "ca.key")
    ca_crt_path = os.path.join(CERTIFICATES_PATH, "ca.pem")

    # Load CA private key
    with open(ca_key_path, "rb") as f:
        ca_private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )

    # Load CA certificate
    with open(ca_crt_path, "rb") as f:
        ca_certificate = x509.load_pem_x509_certificate(f.read())

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save private key
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Generate CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"PT"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Lisbon"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Lisbon"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"FREE"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"PROXY"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"ProxyForApparatusID_{apparatus_id}"),
    ])).sign(private_key, hashes.SHA256())

    # Generate certificate
    certificate = x509.CertificateBuilder().subject_name(
        csr.subject
    ).issuer_name(
        ca_certificate.subject
    ).public_key(
        csr.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Certificate is valid for 1 year
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(f"ProxyForApparatusID_{apparatus_id}")]),
        critical=False,
    ).sign(ca_private_key, hashes.SHA256())

    # Save certificate
    with open(crt_path, "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))


    with open(key_path, 'r') as key_file:
        key_text = key_file.read()
    with open(crt_path, 'r') as crt_file:
        cert_text = crt_file.read()

    return key_text, cert_text
