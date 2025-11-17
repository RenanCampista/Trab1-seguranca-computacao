FROM nginx:alpine

# Esses COPY são opcionais porque você já monta volume,
# mas mantém assim que funciona:
COPY nginx_site/html/ /usr/share/nginx/html/
COPY docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

