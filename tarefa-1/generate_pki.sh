#!/usr/bin/env bash
set -e

echo "[1] Limpando PKI antiga..."
rm -rf pki
mkdir -p pki/root/{certs,private} pki/intermediate/{certs,csr,private} pki/server

#######################
# ROOT CA (CA:true)
#######################
echo "[2] Gerando ROOT CA..."

openssl genrsa -out pki/root/private/ca.key.pem 4096

openssl req -x509 -new \
  -key pki/root/private/ca.key.pem \
  -sha256 -days 3650 \
  -subj "/C=BR/ST=ES/O=MinhaCA/CN=Minha Root CA" \
  -out pki/root/certs/ca.cert.pem

# extensões de CA para a root (re-assina sobre ela mesma com extfile)
cat > pki/root/root_ext.cnf << 'EOR'
basicConstraints=critical,CA:true
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
EOR
openssl x509 -in pki/root/certs/ca.cert.pem -out pki/root/certs/ca.tmp.pem \
  -extfile pki/root/root_ext.cnf -days 3650 -sha256
mv pki/root/certs/ca.tmp.pem pki/root/certs/ca.cert.pem

############################
# INTERMEDIÁRIA (CA:true)
############################
echo "[3] Gerando CA Intermediária..."

openssl genrsa -out pki/intermediate/private/intermediate.key.pem 4096

openssl req -new \
  -key pki/intermediate/private/intermediate.key.pem \
  -out pki/intermediate/csr/intermediate.csr.pem \
  -subj "/C=BR/ST=ES/O=MinhaCA/CN=Minha Intermediaria"

cat > pki/intermediate/intermediate_ext.cnf << 'EOI'
basicConstraints=critical,CA:true,pathlen:0
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
EOI

openssl x509 -req \
  -in pki/intermediate/csr/intermediate.csr.pem \
  -CA pki/root/certs/ca.cert.pem \
  -CAkey pki/root/private/ca.key.pem \
  -CAcreateserial \
  -days 1825 -sha256 \
  -extfile pki/intermediate/intermediate_ext.cnf \
  -out pki/intermediate/certs/intermediate.cert.pem
############################
# CERTIFICADO DO SERVIDOR
############################
echo "[4] Gerando certificado do servidor..."

openssl genrsa -out pki/server/server.key.pem 2048

openssl req -new \
  -key pki/server/server.key.pem \
  -out pki/server/server.csr.pem \
  -subj "/C=BR/ST=ES/O=Servidor/CN=localhost"

cat > pki/server/server_ext.cnf << 'EOS'
basicConstraints=critical,CA:false
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:localhost
EOS

openssl x509 -req \
  -in pki/server/server.csr.pem \
  -CA pki/intermediate/certs/intermediate.cert.pem \
  -CAkey pki/intermediate/private/intermediate.key.pem \
  -CAcreateserial \
  -days 825 -sha256 \
  -extfile pki/server/server_ext.cnf \
  -out pki/server/server.cert.pem
############################
# CADEIA COMPLETA
############################
echo "[5] Montando chain.pem..."

cat pki/server/server.cert.pem \
    pki/intermediate/certs/intermediate.cert.pem \
    pki/root/certs/ca.cert.pem \
    > pki/server/chain.pem

echo "[6] Arquivos finais em pki/server:"
ls -l pki/server

echo "[7] Verificando cadeia com openssl verify..."
openssl verify -CAfile pki/server/chain.pem pki/server/server.cert.pem
