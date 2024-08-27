  ![Python](https://img.shields.io/badge/Python-3.10-blue)   ![Django](https://img.shields.io/badge/Django-4.1.12-brightgreen)   ![MySQL](https://img.shields.io/badge/MySQL-5.7.14-orange)  ![Docker](https://img.shields.io/badge/Docker-24.0.7-blue) ![Docker Compose](https://img.shields.io/badge/Docker%20Compose-1.29.2-blue)  ![Black](https://img.shields.io/badge/Black-23.10.1-black)  ![Ruff](https://img.shields.io/badge/Ruff-0.1.1-lightgrey)  ![Make](https://img.shields.io/badge/Makefile-Yes-green)



# CERMED Gym Admin 

Servicio de Backoffice para la empresa CERMED de Río Cuarto, Córdoba.

## Requisitos del Sistema

- **Python** >= ***3.10***
- **Django** >= ***4.2.12***
- **MySQL** >= ***5.7.14***
- **Docker** >= ***24.0.7***
- **Docker Compose** >= ***1.29.2***
- **Black** >= ***23.10.1***
- **Ruff** >= ***0.1.1***
- **Makefile**


## Instalación

El sistema utiliza **Docker** y **docker-compose** con el objetivo de organizar
y orquestar la estructura. Tenemos 2 contenedores, uno para el servicio de 
la base de datos **MYSQL** y otro para levantar la aplicación de **Django**. También tenemos un 
contenedor para **Nginx**.

1. Clona este repositorio.
2. Crea un entorno virtual: `python3 -m venv venv`.
3. Activa el entorno virtual: `source venv/bin/activate` (Linux/Mac) o `venv\Scripts\activate` (Windows).
4. Instala las dependencias: `pip install -r requirements.txt`
Esto ayudará a que tu `IDE/IDLE` reconozca los paquetes y liberías del proyecto.

## Configuración

1. Copia el archivo de entorno de ejemplo: `cp .env.example .env`
2. Actualiza las variables acorde a tus necesidades y valores.

## Iniciar la Aplicación

1. Levantá y corré los contenedores: `make run`
2. Acá tenés 2 opciones:
  A) Ingresá a la terminal del contenedor `web` para poder crearte un superusuario con`make bash` y luego dentro `python3 gym/manage.py createsuperuser`
  B) Levantá un **backup** que tengas con `make restore` (más detalles en el próximo apartado).
3. Ingresá a `http://localhost:8000/admin/` y empezá a usar el sistema.

## Para producción

En el entorno de producción se utiliza Gunicorn y Nginx para que funcione correctamente en HTTPS.
Para esto, debemos hacer uso de los archivos de configuración de `Dockerfile.prod` y `docker-compose-prod.yaml`,
el `entrypoint-prod.sh` y que se suma un nuevo `service`/contenedor en el `compose` para que corra nginx individualmente.
Nunca está de más checkear los logs en casos de problemas: `docker logs <container_name>`. También
se puede acceder a un `bash` interactivo con `docker exec -it <container_name> /bin/bash`.

También hay que prestar atención al archivo `grupoterraing.conf` ya que contiene la información para el setup
de Nginx. Tener en cuenta variables de entorno siguiendo el `env.example`, los volúmenes y demás. Siguiendo la configuración
actual, simplifico el `down` y el `build up` en 2 comandos `Make`: `make prod-down` y `make prod-up`. 

## Comandos Makefile

- `make build`: Construye los contenedores.
- `make up-d`: Corre los contenedores en modo *detach*.
- `make run`: Construye y corre los contenedores en modo debug.
- `make backup`: Crea un dump de la base de datos.
- `make restore (file=nombre_dump.sql)`: Restaura una versión de la DB a partir de un dump almacenado en la carpeta `backup_data`. Se usa así: `make restore file=dump_file.sql `
- `make bash`: Abre una terminal interactiva dentro del contenedor `web`.

## Contribuciones

Si quieres contribuir, por favor sigue estos pasos:

1. Crea una rama para tu ticket/feature: Desde `master` corré: `git checkout -b "nombre-ticket"`
2. Realiza los cambios y haz commit: `git commit -m "Descripción de los cambios"`
3. Sube los cambios: `git push`
4. Abre un pull request en **GitHub**.

