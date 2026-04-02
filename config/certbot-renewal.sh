#!/bin/sh
# Renueva los certificados Let's Encrypt usando webroot y recarga nginx.

certbot renew --webroot -w /var/www/certbot --quiet

# Recarga nginx para que tome los nuevos certificados
nginx -s reload
