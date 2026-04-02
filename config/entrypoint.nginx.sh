#!/bin/sh
# Entrypoint del contenedor nginx.
# Registra el cronjob de renovacion de certificados e inicia nginx.

# Escribir el cron en /etc/cron.d (idempotente: sobreescribe en cada arranque)
echo "0 3 * * * root /app/config/certbot-renewal.sh >> /var/log/certbot-renewal.log 2>&1" \
    > /etc/cron.d/certbot-renewal
chmod 644 /etc/cron.d/certbot-renewal

# Iniciar el demonio cron en segundo plano
cron

echo "Cron de renovacion de certificados registrado."

# Iniciar nginx en primer plano
exec nginx -g "daemon off;"
