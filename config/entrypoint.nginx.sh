#!/bin/sh
# Entrypoint del contenedor nginx.
# Registra el cronjob de renovacion de certificados e inicia nginx.

# Keep gettext in the C locale and prevent inherited environment overrides from
# satisfying the traversal preconditions of CVE-2026-84243.
export LANG=C.UTF-8
export LANGUAGE=C
export LC_ALL=C.UTF-8

# Escribir el cron en /etc/cron.d (idempotente: sobreescribe en cada arranque)
echo "0 3 * * * root /bin/sh /app/config/certbot-renewal.sh >> /var/log/certbot-renewal.log 2>&1" \
    > /etc/cron.d/certbot-renewal
chmod 644 /etc/cron.d/certbot-renewal

# Iniciar el demonio cron en segundo plano
cron

echo "Cron de renovacion de certificados registrado."

# Iniciar nginx en primer plano
exec nginx -g "daemon off;"
