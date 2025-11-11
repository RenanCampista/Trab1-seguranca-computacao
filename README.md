# Trab1-seguranca-computacao

Este trabalho consolida alguns conceitos estudados na disciplina Segurança em Computação, por meio da implementação de um serviço de certificação digital privado.


## Tarefa 1 – HTTPS com Certificado Válido via CA Privada (Root + Intermediária) usando OpenSSL
TODO


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
1. Navegue até o diretório `tarefa1`:
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
