# Trab1-seguranca-computacao

Este trabalho consolida alguns conceitos estudados na disciplina Segurança em Computação, por meio da implementação de um serviço de certificação digital privado.

## Links Úteis
- [Relatório](relatorio_t1.md)

- [Vídeo da tarefa HTTPS com Certificado Público (Let's Encrypt + ngrok)](https://www.youtube.com/watch?v=lPXP9_PkoKg)

- [Vídeo da tarefa HTTPS com Certificado Válido via CA Privada (Root + Intermediária) usando OpenSSL](https://youtu.be)

- [Vídeo da tarefa HTTPS com Certificado Válido via CA Privada (Root + Intermediária) usando Python](https://youtu.be/xtD6accmXqE)


## Tarefa 1 - HTTPS com Certificado Público (Let's Encrypt + ngrok)
### 1. Requisitos
- Docker e Docker Compose instalados
- `cloudflared` instalado (binário do Cloudflare Tunnel)  
  - Em muitas distros basta: `sudo apt install cloudflared`  
  - Ou baixar direto da página oficial do Cloudflare.
- `curl` (para testes via terminal)

### 2. Subindo o Nginx em HTTP (para validação)
1. Entre na pasta da tarefa:
   ```bash
   cd tarefa1-letsencrypt
   ```

2. Suba o Nginx em background:
    ```bash
    docker-compose up -d --build
    ```

3. Teste o HTTP local:
    ```bash
    curl http://localhost:8081/
    ```

### 3. Criando o túnel público
1. Abra outro terminal e execute:
    ```bash
    cloudflared tunnel --url http://localhost:8081 --protocol http2
    ```

2. O cloudflared abrirá um túnel e exibirá um domínio do tipo:
    ```bash
    chttps://algum-nome-aleatorio.trycloudflare.com
    ```

### 4. Emitindo o certificado com o Certbot (Let’s Encrypt)
1. Execute o Certbot em modo webroot usando Docker:
    ```bash
    docker-compose run --rm certbot certonly \
      --webroot -w /var/www/certbot \
      -d DOMÍNIO-GERADO
    ```

2. O Certbot pedirá um e-mail e confirmação dos termos da Let’s Encrypt.
Depois de alguns segundos, a saída deve indicar sucesso e informar:
- caminho do fullchain.pem
- caminho do privkey.pem

3. Esses caminhos estão dentro do container, mas mapeados para o host em
certbot/conf/live/.... Para facilitar a configuração do Nginx, copie os arquivos para nomes genéricos:
    ```bash
    cp certbot/conf/live/DOMINIO-GERADO/fullchain.pem certbot/conf/live/fullchain.pem
    cp certbot/conf/live/DOMINIO-GERADO/privkey.pem   certbot/conf/live/privkey.pem
    ```

### 5. Testar no navegador
1. Abrir https://DOMINIO-GERADO no navegador → ver página da tarefa com cadeado Let’s Encrypt.


## Tarefa 1 - HTTPS com Certificado Válido via CA Privada (Root + Intermediária) usando OpenSSL e Docker

### Instalação das Dependências
Nenhuma dependência adicional é necessária além de:

- Docker  
- Docker Compose  
- OpenSSL (já presente no Linux)

---

### Execução da Tarefa
1. Navegue até o diretório `tarefa-1`:
   ```bash
   cd tarefa-1
   ```

#### Os passos de 2 a 5 podem ser executados de uma vez através do script:
```bash
./generate_pki.sh
```
Caso queira executar passo a passo, siga as instruções abaixo:

2. Gere a CA raiz:
    ```bash
    openssl req -x509 -new -nodes \
      -keyout pki/root/private/ca.key.pem \
      -out   pki/root/certs/ca.cert.pem \
      -sha256 -days 3650 \
      -subj "/C=BR/ST=ES/O=MinhaCA/CN=Minha Root CA"
    ```
    Isso criará `pki/root/private/ca.key.pem` e `pki/root/certs/ca.cert.pem`

3. Gere a CA intermediária (assinada pela raiz)
    Gerar chave + CSR:
    ```bash
    openssl req -new \
      -keyout pki/intermediate/private/intermediate.key.pem \
      -out   pki/intermediate/csr/intermediate.csr.pem \
      -subj "/C=BR/ST=ES/O=MinhaCA/CN=Minha Intermediaria"
    ```
    Assinar com a Root:
    ```bash
    openssl x509 -req \
      -in  pki/intermediate/csr/intermediate.csr.pem \
      -CA  pki/root/certs/ca.cert.pem \
      -CAkey pki/root/private/ca.key.pem \
      -CAcreateserial \
      -sha256 -days 1825 \
      -out pki/intermediate/certs/intermediate.cert.pem
    ```
    Isso criará `pki/intermediate/private/intermediate.key.pem` e `pki/intermediate/certs/intermediate.cert.pem`

4. Gere e emita o certificado do servidor
    Gerar CSR + chave:
    ```bash
    openssl req -new \
      -keyout pki/server/server.key.pem \
      -out   pki/server/server.csr.pem \
      -subj "/C=BR/ST=ES/O=Servidor/CN=localhost"
    ```
    Assinar com a CA intermediária:
    ```bash
    openssl x509 -req \
      -in  pki/server/server.csr.pem \
      -CA  pki/intermediate/certs/intermediate.cert.pem \
      -CAkey pki/intermediate/private/intermediate.key.pem \
      -CAcreateserial \
      -sha256 -days 825 \
      -out pki/server/server.cert.pem
    ```
    Criar fullchain:
    ```bash
    cat pki/server/server.cert.pem \
      pki/intermediate/certs/intermediate.cert.pem \
      pki/root/certs/ca.cert.pem \
     > pki/server/chain.pem
    ```
    Serão criados `pki/server/server.key.pem`, `pki/server/server.csr.pem`, `pki/server/server.cert.pem` e `pki/server/chain.pem`

    O servidor estará disponível em:
    - HTTPS: https://localhost:4443
    - HTTP: http://localhost:8001

### Teste (no host)
#### Usando curl com a CA raiz:
    ```bash
    curl -v --cacert pki/root/certs/ca.cert.pem https://localhost:4443/
    ```
    Se a cadeia estiver correta, o resultado será:
    ```nginx
    SSL certificate verify ok.
    HTTP/1.1 200 OK
    ```
    Sem --cacert, o curl irá recusar, pois a CA é privada.

#### Importar CA Raiz no navegador (para confiar permanentemente)
    Exemplo com Firefox (os outros são semelhantes):
1. Abra:
    Preferences → Privacy & Security → Certificates → View Certificates... → Authorities → Import
2. Selecione:
    ```bash
    pki/root/certs/ca.cert.pem
    ```
3. Marque `Trust this CA to identify websites`
4. Acesse:
    ```bash
    https://localhost:4443/
    ```
    Deve aparecer o cadeado, indicando conexão segura



## Tarefa 2 - HTTPS com Certificado Válido via CA Privada (Root + Intermediária) usando Python
### Instalação das Dependências
1. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows use `venv\Scripts\activate`
   ```
2. Instale as dependências necessárias:
   ```bash
    cd tarefa2
    pip install -r requirements.txt
    ```
### Execução do Servidor HTTPS
1. Navegue até o diretório `tarefa2`:
   ```bash
   cd tarefa2
   ```

   
#### Os passos de 2 a 5 podem ser executados de uma vez através do makefile, com o comando:
```bash
make all
```
Caso queira executar passo a passo, siga as instruções abaixo:


2. Gere a CA raiz:
    ```bash
    python3 scripts/create_root_ca.py
    ```
    Isso criará `certs/root/root.key.pem` e `certs/root/root.cert.pem`.

3. Gere a CA intermediária (assinada pela raiz):
    ```bash
    python3 scripts/create_intermediate_ca.py
    ```
    Isso criará `certs/intermediate/inter.key.pem` e `inter.cert.pem`.

4. Gere e emita o certificado do servidor:
    ```bash
    python3 scripts/issue_server_cert.py
    ```
    Isso criará `certs/server/server.key.pem`, `server.csr.pem`, `server.cert.pem` e `fullchain.pem`.

5. Inicie o container nginx com Docker Compose:
    ```bash
    cd docker && docker-compose up --build
    ```


### Teste (no host)
#### Usando curl com a CA raiz:
```bash
curl -v --cacert certs/root/root.cert.pem https://localhost:8443/
```
Se a cadeia estiver correta e você passar o certificado da raiz para curl, deve retornar a página HTML. Sem `--cacert` o curl vai recusar por não confiar na CA.

#### Importar CA Raiz no navegador (para confiar permanentemente)
Será utilizado o navegador Firefox como exemplo, mas o processo é similar em outros navegadores.

1. Abra Preferences (Preferências) → Privacy & Security → Certificates → View Certificates... → aba Authorities → Import

2. Selecione o arquivo `certs/root/root.cert.pem` e importe.

3. Marque a opção "Trust this CA to identify websites" (Confiar nesta CA para identificar sites) e clique em OK.

4. Agora abra https://localhost:8443/ — o Firefox deve mostrar como seguro (mostrar o cadeado).
