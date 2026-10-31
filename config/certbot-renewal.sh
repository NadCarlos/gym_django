#!/bin/sh
# Renueva los certificados Let's Encrypt usando webroot y recarga nginx.
set -eu

/usr/bin/certbot renew --webroot -w /var/www/certbot --quiet

# Recarga nginx para que tome los nuevos certificados
/usr/sbin/nginx -t
/usr/sbin/nginx -s reload
