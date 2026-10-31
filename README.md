![Python](https://img.shields.io/badge/Python-3.12.16-blue) ![Django](https://img.shields.io/badge/Django-5.2.18-brightgreen) ![MySQL](https://img.shields.io/badge/MySQL-8.4.13-orange)



# CERMED Gym Admin 

Servicio de Backoffice para la empresa CERMED de Río Cuarto, Córdoba.

## Requisitos del Sistema

- Python 3.12.16, Django 5.2.18 LTS y MySQL 8.4.13 LTS.
- Docker Engine, Docker Compose v2 con `up --wait`, y Make.
- Dependencias exactas y hashes en `requirements-prod.txt` (runtime) y `requirements.txt` (desarrollo).

Producción ya corre con este stack. El historial, los respaldos y el procedimiento
de recuperación de la migración están en [UPGRADE-2026.md](UPGRADE-2026.md).

## Instalación

El stack local y de producción se ejecuta con Docker Compose: Django 5.2.18 sobre
Python 3.12.16, MySQL 8.4.13 y Nginx. En producción, Gunicorn sirve Django detrás
de Nginx con HTTPS. Las dependencias de producción y desarrollo están fijadas con
hashes en `requirements-prod.txt` y `requirements.txt`, respectivamente.

1. Clona este repositorio.
2. Crea un entorno virtual: `python3 -m venv venv`.
3. Activa el entorno virtual: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows).
4. Instala las dependencias: `pip install --require-hashes -r requirements.txt`
Esto ayudará a que tu `IDE/IDLE` reconozca los paquetes y liberías del proyecto.

## Configuración

1. Copia el archivo de entorno de ejemplo: `cp .env.example .env`
2. Actualiza las variables acorde a tus necesidades y valores.
3. Generá TLS con `bash scripts/create-mysql-tls.sh /ruta/privada/nueva HOST_DB`,
   usando el nombre de `MYSQL_HOST`, y guardá esa ruta en `CERMED_MYSQL_TLS_DIR`
   de `.env`. Requiere Bash, OpenSSL y GNU realpath. Las claves deben quedar fuera
   del repositorio. Ver [preparación y renovación TLS](UPGRADE-2026.md#preparar-tls-de-mysql).

## Iniciar la Aplicación

1. Levantá y corré los contenedores: `make run`
2. Acá tenés 2 opciones:
  A) Ingresá a la terminal del contenedor `web` para poder crearte un superusuario con`make bash` y luego dentro `python3 gym/manage.py createsuperuser`
  B) Levantá un **backup** que tengas con `make restore` (más detalles en el próximo apartado).
3. Ingresá a `http://localhost:8000/admin/` y empezá a usar el sistema.

## Para producción

En producción se utilizan `Dockerfile.prod`, `Dockerfile.mysql`, `Dockerfile.nginx`
y `docker-compose-prod.yaml`. La configuración toma variables de `.env.prod`, que
existe únicamente en el servidor. Los targets `prod-*` del `Makefile` operan el stack.
Nunca está de más checkear los logs en casos de problemas: `docker logs <container_name>`. También
se puede acceder a un `bash` interactivo con `docker exec -it <container_name> /bin/bash`.

La configuración de Nginx está en `cermed.conf`. Consultá `.env.example` para las
variables locales; nunca guardes `.env.prod` en Git.

## CI/CD producción

El CI se ejecuta con GitHub Actions en cada push a `develop` y `production`.
En `production`, CI valida tests, migraciones, estáticos, dependencias e imágenes. El deploy por SSH solo se habilita cuando la variable de repositorio `CERMED_MYSQL84_READY` vale `true`, después de validar la migración. El archivo `.env.prod` debe existir únicamente en el servidor e indicar `CERMED_MYSQL84_VOLUME`, el volumen 8.4 restaurado.

Secrets requeridos en GitHub:

- `PROD_HOST`: IP o dominio del servidor.
- `PROD_USER`: usuario SSH con permisos para operar el repo y Docker.
- `PROD_SSH_KEY`: clave privada SSH para deploy.
- `PROD_APP_DIR`: ruta absoluta del repo en el servidor.

Secrets opcionales:

- `PROD_SSH_PORT`: puerto SSH. Si no se define, usa `22`.
- `PROD_HEALTHCHECK_URL`: URL que se consulta desde el servidor al final del deploy. Si no se define, usa `http://localhost:8000/`.

Para el historial de despliegue y recuperación, consultá [UPGRADE-2026.md](UPGRADE-2026.md).
El workflow conserva el despliegue SSH + git/Compose y bloquea High/Critical del
escaneo de imágenes. Un `check --deploy` con advertencias no equivale a una
configuración productiva completamente endurecida.

La reversión de MySQL necesita el volumen y las imágenes anteriores, además del
código. Seguir la sección de corte y reversión del runbook; volver solo el commit
no revierte una migración de datos.

## Comandos Makefile

- `make build`: Construye los contenedores.
- `make up-d`: Corre los contenedores en modo *detach*.
- `make run`: Construye y corre los contenedores en modo debug.
- `make prod-config`: Valida la configuración efectiva de Docker Compose para producción.
- `make prod-deploy`: Construye y levanta el stack productivo en modo *detach*.
- `make prod-status`: Muestra el estado de los servicios productivos.
- `make backup`: Crea un dump de la base de datos.
- `make restore (file=nombre_dump.sql)`: Restaura una versión de la DB a partir de un dump almacenado en la carpeta `backup_data`. Se usa así: `make restore file=dump_file.sql `
- `make bash`: Abre una terminal interactiva dentro del contenedor `web`.

## Contribuciones

Si quieres contribuir, por favor sigue estos pasos:

1. Crea una rama para tu ticket/feature: Desde `master` corré: `git checkout -b "nombre-ticket"`
2. Realiza los cambios y haz commit: `git commit -m "Descripción de los cambios"`
3. Sube los cambios: `git push`
4. Abre un pull request en **GitHub**.

