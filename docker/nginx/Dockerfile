# docker/nginx/Dockerfile
FROM nginx:stable-alpine

# Copia configuração customizada do nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copia site estático
COPY ../../nginx_site/html /usr/share/nginx/html

# Certs serão montadas via volume no docker-compose em /etc/nginx/certs
# (não copiamos os certificados aqui por segurança; usamos volumes)
