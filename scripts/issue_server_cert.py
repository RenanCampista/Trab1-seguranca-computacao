"""
Gera chave do servidor, CSR com SAN (localhost, 127.0.0.1),
assina com a CA Intermediária e exporta:
 - certs/server/server.key.pem
 - certs/server/server.csr.pem
 - certs/server/server.cert.pem
 - certs/server/fullchain.pem (server + intermediate)
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import DNSName, IPAddress
from datetime import datetime, timedelta
import ipaddress
import os

ROOT_CERT = os.path.join(os.path.dirname(__file__), '..', 'certs', 'root', 'root.cert.pem')
INTER_KEY = os.path.join(os.path.dirname(__file__), '..', 'certs', 'intermediate', 'inter.key.pem')
INTER_CERT = os.path.join(os.path.dirname(__file__), '..', 'certs', 'intermediate', 'inter.cert.pem')

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs', 'server')
os.makedirs(OUT_DIR, exist_ok=True)

# Ler chave e cert da CA intermediária
with open(INTER_KEY, 'rb') as f:
    inter_key = serialization.load_pem_private_key(f.read(), password=None)

with open(INTER_CERT, 'rb') as f:
    inter_cert = x509.load_pem_x509_certificate(f.read())

# Gerar chave privada do servidor (RSA 4096)
srv_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

# Construir subject do servidor (CN = localhost)
srv_subject = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Meu Servidor Local"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
])

# Construir CSR com SANs
csr_builder = (
    x509.CertificateSigningRequestBuilder()
    .subject_name(srv_subject)
    .add_extension(
        x509.SubjectAlternativeName([
            DNSName(u"localhost"),
            IPAddress(ipaddress.IPv4Address("127.0.0.1"))
        ]),
        critical=False
    )
)
csr = csr_builder.sign(srv_key, hashes.SHA256())

# Assinar CSR com a CA intermediária (emitir certificado de servidor)
cert_builder = (
    x509.CertificateBuilder()
    .subject_name(csr.subject)
    .issuer_name(inter_cert.subject)
    .public_key(csr.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow() - timedelta(days=1))
    .not_valid_after(datetime.utcnow() + timedelta(days=825))  # ~2 anos, ajustar se quiser
    .add_extension(
        x509.SubjectAlternativeName([
            DNSName(u"localhost"),
            IPAddress(ipaddress.IPv4Address("127.0.0.1"))
        ]),
        critical=False
    )
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
    .add_extension(x509.KeyUsage(digital_signature=True,
                                 key_encipherment=True,
                                 key_cert_sign=False,
                                 key_agreement=False,
                                 content_commitment=False,
                                 data_encipherment=False,
                                 encipher_only=False,
                                 decipher_only=False,
                                 crl_sign=False), critical=True)
)

srv_cert = cert_builder.sign(private_key=inter_key, algorithm=hashes.SHA256())

# Exportar chave, csr, cert
key_path = os.path.join(OUT_DIR, 'server.key.pem')
csr_path = os.path.join(OUT_DIR, 'server.csr.pem')
cert_path = os.path.join(OUT_DIR, 'server.cert.pem')
fullchain_path = os.path.join(OUT_DIR, 'fullchain.pem')

with open(key_path, 'wb') as f:
    f.write(srv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ))

with open(csr_path, 'wb') as f:
    f.write(csr.public_bytes(serialization.Encoding.PEM))

with open(cert_path, 'wb') as f:
    f.write(srv_cert.public_bytes(serialization.Encoding.PEM))

# Criar fullchain.pem = server cert + intermediate cert (neste ordem)
with open(fullchain_path, 'wb') as f:
    f.write(srv_cert.public_bytes(serialization.Encoding.PEM))
    with open(INTER_CERT, 'rb') as ic:
        f.write(ic.read())

print(f"Server key: {key_path}")
print(f"Server CSR: {csr_path}")
print(f"Server cert: {cert_path}")
print(f"Full chain: {fullchain_path}")
