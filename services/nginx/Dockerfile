# docker context should be the repo root

FROM nginx:latest

COPY ./services/nginx/config/ /etc/nginx/conf.d/
COPY ./frontend/dist/ /var/www/
