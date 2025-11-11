# Makefile para automação da PKI + Nginx HTTPS local

PYTHON := python
SCRIPTS_DIR := scripts
CERTS_DIR := certs
DOCKER_DIR := docker

.PHONY: all clean certs docker up down rebuild


all: certs up
	@echo "Ambiente HTTPS rodando em https://localhost:8443"
	@echo "   Use 'make down' para parar o container."


certs: root_ca intermediate_ca server_cert
	@echo "Certificados gerados com sucesso em ./certs/"

root_ca:
	@echo "Gerando CA Raiz..."
	@$(PYTHON) $(SCRIPTS_DIR)/create_root_ca.py

intermediate_ca:
	@echo "Gerando CA Intermediária..."
	@$(PYTHON) $(SCRIPTS_DIR)/create_intermediate_ca.py

server_cert:
	@echo "Gerando certificado do servidor..."
	@$(PYTHON) $(SCRIPTS_DIR)/issue_server_cert.py


docker:
	@echo "Construindo imagem Docker..."
	@cd $(DOCKER_DIR) && docker-compose build

up:
	@echo "Subindo container Nginx com HTTPS..."
	@cd $(DOCKER_DIR) && docker-compose up -d

down:
	@echo "Parando container Nginx..."
	@cd $(DOCKER_DIR) && docker-compose down

rebuild:
	@echo "Recriando ambiente Docker..."
	@$(MAKE) down
	@$(MAKE) docker
	@$(MAKE) up


clean:
	@echo "Removendo certificados e pastas geradas..."
	@rm -rf $(CERTS_DIR)/root $(CERTS_DIR)/intermediate $(CERTS_DIR)/server
	@echo "Limpeza concluída."


help:
	@echo "Comandos disponíveis:"
	@echo "  make all           -> Gera tudo e inicia o servidor HTTPS"
	@echo "  make certs         -> Gera apenas as CAs e o certificado do servidor"
	@echo "  make docker        -> Constrói a imagem Docker"
	@echo "  make up            -> Sobe o container nginx"
	@echo "  make down          -> Para o container nginx"
	@echo "  make rebuild       -> Reconstrói todo o ambiente"
	@echo "  make clean         -> Remove todos os certificados gerados"
	@echo "  make help          -> Mostra esta ajuda"
