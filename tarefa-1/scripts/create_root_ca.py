"""
Gera a CA Raiz (chave RSA 4096 + certificado autoassinado).
Saída:
 - certs/root/root.key.pem  (chave privada PEM)
 - certs/root/root.cert.pem (certificado PEM)
"""
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs', 'root')
os.makedirs(OUT_DIR, exist_ok=True)

# Gerar chave privada RSA 4096
key = rsa.generate_private_key(public_exponent=65537, key_size=4096)

# Construir subject e issuer (iguais para autoassinada)
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Espírito Santo"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"Vitória"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Minha CA de Teste"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"My Test Root CA"),
])

# Construir certificado autoassinado
cert_builder = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.now(timezone.utc) - timedelta(days=1))
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650))  # 10 anos
    # Indica que este é CA (basicConstraints)
    .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
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

cert = cert_builder.sign(private_key=key, algorithm=hashes.SHA256())

# Exportar arquivos PEM
key_path = os.path.join(OUT_DIR, 'root.key.pem')
cert_path = os.path.join(OUT_DIR, 'root.cert.pem')

with open(key_path, 'wb') as f:
    f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # PKCS#1
        encryption_algorithm=serialization.NoEncryption()
    ))

with open(cert_path, 'wb') as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print(f"Root key: {key_path}")
print(f"Root cert: {cert_path}")
