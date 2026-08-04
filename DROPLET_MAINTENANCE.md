# Mantenimiento del droplet de produccion

Guia operativa para mantener estable un droplet chico, evitar que Docker llene el disco y detectar problemas antes de que afecten produccion.

## Estado base actual

Ultima referencia medida:

- Disco root: `25G` total, `11G` usado, `14G` libre, `45%` de uso.
- Docker images: `3.254GB`, con `760.9MB` reclaimable.
- Containers: `3` activos, sin espacio reclaimable relevante.
- Volumenes Docker: `1` activo, `252.5MB`.
- Build cache: `905.1MB`, con `169MB` reclaimable.
- RAM: `957Mi` total, `369Mi` available.
- Swap: `2.0Gi`, con `16Mi` usado.

Ese estado esta sano. No hace falta limpieza agresiva.

## Checks rapidos

Ejecutar cuando se quiera revisar salud general:

```bash
df -h
docker system df
free -h
sudo journalctl --disk-usage
```

Lectura practica:

- Disco menor a `75%`: normal.
- Disco entre `75%` y `85%`: revisar Docker, logs y backups.
- Disco mayor a `85%`: limpiar y actuar antes de deployar.
- Swap mayor a `500MB` de forma sostenida: revisar memoria/procesos.
- Volumen MySQL creciendo de golpe: revisar tablas, backups o logs inesperados.

## Log rotation de Docker

Evita que los logs JSON de Docker crezcan sin limite.

Crear o editar:

```bash
sudo nano /etc/docker/daemon.json
```

Contenido recomendado:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Aplicar:

```bash
sudo systemctl restart docker
```

Nota: reinicia Docker y puede reiniciar contenedores. Hacerlo en horario tranquilo.

## Limpieza segura de Docker

Comandos seguros para limpiar imagenes viejas, contenedores parados y build cache sin tocar volumenes:

```bash
docker system prune -af --filter "until=168h"
docker builder prune -af --filter "until=168h"
```

No usar en produccion salvo que estes completamente seguro:

```bash
docker system prune --volumes
```

`--volumes` puede borrar volumenes importantes, incluido MySQL si queda no referenciado.

## Limpieza semanal con cron

Crear script:

```bash
sudo nano /usr/local/bin/docker-safe-prune.sh
```

Contenido:

```bash
#!/usr/bin/env bash
set -euo pipefail

docker system prune -af --filter "until=168h"
docker builder prune -af --filter "until=168h"
```

Permisos:

```bash
sudo chmod +x /usr/local/bin/docker-safe-prune.sh
```

Cron semanal, por ejemplo domingos 03:30:

```bash
sudo crontab -e
```

Agregar:

```cron
30 3 * * 0 /usr/local/bin/docker-safe-prune.sh >> /var/log/docker-safe-prune.log 2>&1
```

## Backups del proyecto

Revisar peso de backups:

```bash
cd <PROD_APP_DIR>
du -sh backup_data gym/backup_data 2>/dev/null
```

Eliminar backups con mas de 14 dias:

```bash
cd <PROD_APP_DIR>
find backup_data gym/backup_data -type f -mtime +14 -delete
```

Si se quiere automatizar, agregar al cron semanal despues del prune:

```cron
45 3 * * 0 cd <PROD_APP_DIR> && find backup_data gym/backup_data -type f -mtime +14 -delete >> /var/log/backup-retention.log 2>&1
```

Ajustar `14` segun la retencion que se quiera.

## Logs del sistema Ubuntu

Ver uso actual:

```bash
sudo journalctl --disk-usage
```

Limpiar logs viejos manualmente:

```bash
sudo journalctl --vacuum-time=7d
```

Limitar journald de forma permanente:

```bash
sudo nano /etc/systemd/journald.conf
```

Setear o descomentar:

```ini
SystemMaxUse=200M
MaxRetentionSec=7day
```

Aplicar:

```bash
sudo systemctl restart systemd-journald
```

## Swap y memoria

Ver memoria:

```bash
free -h
```

Estado recomendado para droplet de 1GB:

- Tener `1G` o `2G` de swap.
- Swap casi vacia o con uso bajo: normal.
- Swap alta de forma sostenida: revisar procesos, Gunicorn workers, MySQL y cron jobs.

Ver procesos que mas memoria usan:

```bash
ps aux --sort=-%mem | head -15
```

## Seguridad basica

Firewall minimo:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
sudo ufw status
```

Fail2ban:

```bash
sudo apt update
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
sudo systemctl status fail2ban
```

## Checklist antes/despues de deploy

Antes:

```bash
df -h
docker system df
free -h
```

Despues:

```bash
cd <PROD_APP_DIR>
make prod-status
docker logs cermed_web --tail 100
docker logs cermed_nginx --tail 100
```

Si el disco sube mucho despues de deploys repetidos:

```bash
docker system df
docker system prune -af --filter "until=168h"
docker builder prune -af --filter "until=168h"
docker system df
```

## Que evitar

- No correr `docker system prune --volumes` como limpieza rutinaria.
- No borrar manualmente carpetas dentro de `/var/lib/docker`.
- No borrar `.env.prod`.
- No limpiar backups sin verificar que exista al menos una copia recuperable.
- No reiniciar Docker en horario pico si no es necesario.

## Comando de diagnostico completo

Para copiar y pegar cuando haya que revisar estado:

```bash
set -e
printf '\n== Disk ==\n'
df -h
printf '\n== Docker disk ==\n'
docker system df
printf '\n== Memory ==\n'
free -h
printf '\n== Journald ==\n'
sudo journalctl --disk-usage
printf '\n== Biggest paths in repo ==\n'
cd <PROD_APP_DIR>
du -h --max-depth=2 . 2>/dev/null | sort -h | tail -20
```
