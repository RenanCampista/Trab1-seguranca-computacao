# Makefile para a Tarefa 1 - HTTPS público com Nginx + Cloudflare Tunnel
# Diretório base: tarefa-1/

DOCKER_DIR      := docker
COMPOSE_FILE    := $(DOCKER_DIR)/docker-compose.yml
COMPOSE         := docker-compose -f $(COMPOSE_FILE)

# Porta HTTP interna exposta pelo container (mapeada em 8001 no host)
APP_PORT        := 8001

.PHONY: help build up down restart logs ps curl-local tunnel clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make build        - Build da imagem Docker do Nginx"
	@echo "  make up           - Sobe o container em background"
	@echo "  make down         - Para e remove o container"
	@echo "  make restart      - Reinicia o container (down + up)"
	@echo "  make logs         - Mostra logs do container (seguindo)"
	@echo "  make ps           - Lista containers do projeto"
	@echo "  make curl-local   - Testa o acesso HTTP local (localhost:$(APP_PORT))"
	@echo "  make tunnel       - Abre o Cloudflare Tunnel para o Nginx (usa cloudflared)"
	@echo "  make clean        - Remove containers e imagens do projeto"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart: down up

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

curl-local:
	curl -v http://localhost:$(APP_PORT) || true

# IMPORTANTE:
# Este alvo abre o túnel Cloudflare e bloqueia o terminal.
# Deixe este 'make tunnel' rodando em UMA aba de terminal
# e acesse o domínio que o cloudflared mostrar em outra.
tunnel:
	cloudflared tunnel --url http://localhost:$(APP_PORT)

# Remove containers e imagens relacionadas ao projeto
clean:
	$(COMPOSE) down --rmi local --volumes --remove-orphans
