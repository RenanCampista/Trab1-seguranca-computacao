"""
Gera a CA Intermediária (chave RSA 4096 + certificado assinado pela CA Raiz).
Entrada: certs/root/root.key.pem, certs/root/root.cert.pem
Saída:
 - certs/intermediate/inter.key.pem
 - certs/intermediate/inter.cert.pem
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import os

ROOT_KEY = os.path.join(os.path.dirname(__file__), '..', 'certs', 'root', 'root.key.pem')
ROOT_CERT = os.path.join(os.path.dirname(__file__), '..', 'certs', 'root', 'root.cert.pem')

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs', 'intermediate')
os.makedirs(OUT_DIR, exist_ok=True)

# Ler chave raiz
with open(ROOT_KEY, 'rb') as f:
    root_key = serialization.load_pem_private_key(f.read(), password=None)

with open(ROOT_CERT, 'rb') as f:
    root_cert = x509.load_pem_x509_certificate(f.read())

# Gerar chave da intermediária
inter_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

# Subject da intermediária
inter_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Minha CA Intermediária"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"My Test Intermediate CA"),
])

# Criar o certificado da intermediária assinado pela raiz
builder = (
    x509.CertificateBuilder()
    .subject_name(inter_subject)
    .issuer_name(root_cert.subject)
    .public_key(inter_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # 10 anos de validade
    .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
    .add_extension(x509.KeyUsage(digital_signature=False,
                                 key_encipherment=False,
                                 key_cert_sign=True,
                                 key_agreement=False,
                                 content_commitment=False,
                                 data_encipherment=False,
                                 encipher_only=False,
                                 decipher_only=False,
                                 crl_sign=True), critical=True)
)

inter_cert = builder.sign(private_key=root_key, algorithm=hashes.SHA256())

# Exportar chave e certificado da intermediária
key_path = os.path.join(OUT_DIR, 'inter.key.pem')
cert_path = os.path.join(OUT_DIR, 'inter.cert.pem')

with open(key_path, 'wb') as f:
    f.write(inter_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open(cert_path, 'wb') as f:
    f.write(inter_cert.public_bytes(serialization.Encoding.PEM))

print(f"Intermediate key: {key_path}")
print(f"Intermediate cert: {cert_path}")
