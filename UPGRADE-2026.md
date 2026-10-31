# Actualización preventiva de CERMED — 24/10/2026

**Estado al 31/10: producción migrada y reabierta en `7883216`.** El usuario
confirmó el sistema funcionando con Python 3.12.16, Django 5.2.18, MySQL 8.4.13 y
Nginx 1.31.8. Login y estáticos devolvieron HTTPS 200 con certificado válido tanto
en el droplet como desde una comprobación externa. CI del release pasó.
`CERMED_MYSQL84_READY=true` quedó habilitado para los futuros despliegues por
SSH + git/Compose; habilitar la variable no ejecutó otro despliegue.

El corte conservó **`gym_db`, `bunfer` y `bunfercopia2`**. Las dos últimas parecen
copias de otros sistemas según el usuario, pero su desuso no está confirmado:
no eliminarlas. El backup final se restauró secuencialmente en volúmenes nuevos
8.0 y 8.4. Coincidieron tablas, conteos, hashes de filas, resultados de vistas,
motores y collations; se repitió la comparación tras reiniciar y al conectar el
volumen 8.4 a Compose. La importación preservó la collation de 5.7 mediante una
opción de sesión, sin cambiar el default global del servidor nuevo.

- Volumen productivo: `cermed_mysql84_20261031_sp3xsl01`.
- Volumen 5.7 retenido: `gym_django_db_data`; nunca montarlo con MySQL 8.x.
- Artefactos privados del corte:
  `/home/cermed/cermed-upgrade-backups/release-20261031T031935Z.sP3XSL01`.
  **`mysql-tls/` dentro de ese directorio está en uso por producción**, no es
  caché descartable. `data/final57.sql` incluye las tres bases y
  `data/media-static.tar` conserva medios y estáticos; checksums verificados.
- Pasaron checks de Django, ausencia de migraciones pendientes y drift,
  collectstatic, backup con el usuario real y TLS verificado, login y estáticos.
  Ambos procesos cron quedaron activos. La renovación ACME staging ya había
  pasado antes del corte; no se volvió a ejecutar durante esta activación.
- Se generó `backup_data/cermed-first84-sp3xsl01.sql` con Django en producción.
  La restauración de **ese nuevo dump** y la copia externa del backup final del
  corte aún no están confirmadas; no confundirlas con los ensayos previos.
  Cron ejecuta el backup a las 02:00 UTC (23:00 de Argentina), aunque Django usa
  la zona argentina. El inventario posterior solo encontró el backup manual de
  hoy y automáticos hasta septiembre de 2025; `daily_database_backup` oculta las
  excepciones. Aún hay que verificar la ejecución automática de la versión nueva.
- Estado inmediato: disco libre 3.5 GiB (86% usado), RAM disponible 158 MiB y
  swap usada 92 MiB. Es una medición inicial, no una prueba de estabilidad.
- En la reapertura, `check --deploy` informó `urls.W010` por el `<` sobrante en
  `gym/administracion/urls.py`, ruta `error_profesional_existente`; no bloqueó el
  despliegue. La corrección está en `ca72117`, con cuatro tests de administración
  y comprobaciones de resolución y autenticación aprobados. La aceptación
  detallada de agendas/pagos y el backup nocturno quedan para el seguimiento.
- Tras un reinicio del droplet confirmado por el usuario, se eliminó únicamente
  la caché regenerable `cermed-upgrade-grype-cache` (3.376 GB). Quedaron 6.6 GiB
  libres (73% usado); MySQL 214.6 MiB, web 162 MiB, Nginx 7.6 MiB, RAM disponible
  283 MiB, sin OOM ni reinicios automáticos. Imágenes y volúmenes se conservaron.

**Las escrituras ya están habilitadas en 8.4.** Los comandos de rollback del corte
no deben ejecutarse ahora: volver a 5.7 perdería operaciones posteriores y requiere
reconciliación. Se conservaron imágenes anteriores, volumen original y respaldos.
Las secciones numeradas siguientes documentan el procedimiento de la primera
migración; no volver a ejecutarlo sobre esta producción ya migrada.

Persisten 13 CVE High distintos aceptados de forma acotada; no se consideran
corregidos. La política exacta y sus controles están en
`config/reviewed-image-risk.json` y `UPGRADE-IMAGE-TRIAGE.md`.

El alcance acordado es actualizar versiones y validar compatibilidad. El puerto
8000 queda en loopback; 3308, HTTPS, permisos de medios y endpoints se conservan.
La conexión MySQL incorpora TLS verificado; DBeaver debe confiar en la CA privada.
No hay evidencia aportada de compromiso. Un escaneo de dependencias
identifica riesgos conocidos; no demuestra ni descarta una intrusión.

## Versiones y cambios

| Componente | Anterior en el repositorio | Objetivo |
| --- | --- | --- |
| Python | 3.10 | 3.12.16, Debian Trixie slim |
| Django | 4.1.12 | 5.2.18 LTS |
| MySQL | 5.7 | 8.4.13 LTS, pasando por 8.0.46 |
| Nginx | etiqueta mutable; producción 1.31.6 | 1.31.8 |
| Gunicorn | 21.2.0 | 26.2.0 |
| Pillow | dependencia transitiva | 13.0.0 explícita |

Las imágenes base están fijadas por digest. Las dependencias Python están fijadas
con hashes; `requirements-prod.in` contiene las directas y `requirements.in`
agrega herramientas de desarrollo. Los paquetes sin uso en imports/configuración
se retiraron del runtime. Los compiladores quedan en una etapa de construcción.
Los paquetes Debian se actualizan al construir; registrar el ID de la imagen
construida, porque sus repositorios cambian aunque el digest base sea fijo.
`Dockerfile.mysql` conserva MySQL 8.4.13, actualiza los certificados del sistema
y retira MySQL Shell, que CERMED no utiliza. `mysql` y `mysqldump` permanecen.
El Upgrade Checker se ejecuta aparte con la herramienta oficial; no forma parte
del contenedor que sirve la base.

Las adaptaciones de Django preservan los formatos de números/fechas y el directorio
de backups. `django-dbbackup` utiliza ahora `STORAGES["dbbackup"]`. Se prueban
exportaciones XLSX/PDF, contraseñas anteriores y roles. El comando de tests de CI
ahora enumera las aplicaciones: antes, desde la raíz, descubría cero tests.

## 1. Completar el inventario del droplet

Copiar el contenido de [DROPLET-CHECKS.txt](DROPLET-CHECKS.txt) en la terminal del
servidor. Son comandos de lectura, sin cambios ni credenciales en su salida.
El inventario extendido está en `scripts/upgrade-inventory.sh`; requiere también
`scripts/runtime_inventory.py` junto a él. Se puede copiar ambos archivos sin
hacer `git pull` del cambio en el checkout que sirve producción.

Ya informado: Ubuntu 22.04.5, RAM 957 MiB, swap 2 GiB, disco libre 9.7 GiB.
Están publicados 80/443, 8000 y 3308. Inventario confirmado por el usuario:
Python 3.10.21, Django 4.1.12, MySQL 5.7.44, Nginx 1.31.6, Docker 29.9.2 y
Compose v5.6.1. `/var/lib/mysql` ocupa 248 MB: incluye archivos del motor, no es
el tamaño exacto del dump. Pillow 12.3.0, certifi 2024.7.4, Gunicorn 21.2.0 y
mysqlclient 2.0.0 también están confirmados. Con esta memoria, el ensayo pesado debe correr localmente;
en el servidor las etapas de bases de datos serán secuenciales.

**Cierre:** registrar versiones, tamaño de datos, espacio para backups/volúmenes,
commit e imágenes actuales. Identificar también cron, accesos DBeaver y cualquier
otro proceso que escriba en la base durante la futura ventana.

## 2. Obtener y proteger un backup real

Copiar todo [DROPLET-BACKUP.txt](DROPLET-BACKUP.txt) en la terminal del droplet,
con la base actual funcionando. Comprueba tablas InnoDB, registra las imágenes
y el volumen original, crea un dump privado y calcula su checksum. Se detiene
ante errores y no presenta un `.partial` como backup válido. Este primer dump
sirve para ensayar; se repetirá con escrituras detenidas para el corte final.

Si el dump falla, detenerse: que el archivo exista no lo vuelve válido.
`--single-transaction` requiere tablas transaccionales para garantizar una vista
consistente; revisar los motores antes del backup final. No usar `--all-databases`
ni restaurar tablas internas `mysql.*` de 5.7 en 8.x. Respaldar también los medios,
`.env.prod` y certificados por un canal privado y verificar su recuperación.
Copiar el SQL fuera del droplet por SSH/SCP y comprobar su SHA-256. No adjuntar
datos de pacientes al chat ni guardarlos dentro del repositorio.

**Cierre:** backup legible, checksum coincidente y copia fuera del servidor.

El usuario ya confirmó la generación del backup de ensayo (62 tablas InnoDB y
4.789.350 bytes); su ubicación, checksum e imágenes originales están en
`UPGRADE-VALIDATION.md`. Para completar la copia externa, ejecutar
[LOCAL-COPY-BACKUP.txt](LOCAL-COPY-BACKUP.txt) **en la computadora local**. El bloque
pide el host SSH, descarga a una carpeta privada fuera del repo y compara tamaño
y SHA-256 con los valores confirmados, antes de continuar con la restauración.
La copia externa y el ensayo real ya se completaron en esta ejecución; el detalle
está en `UPGRADE-VALIDATION.md`. No hace falta repetir la copia para continuar.

## 3. Ensayar MySQL y aplicación en Docker local

El Compose de ensayo no publica puertos ni monta `.env`, medios o datos reales del
proyecto. Usa credenciales desechables y una red interna. No inicia cron ni Sentry.
Ejecutar desde un checkout local del cambio, con una copia privada del backup:

```bash
make upgrade-build
bash scripts/rehearse-mysql-upgrade.sh /ruta/privada/pre-upgrade.sql
make upgrade-check
```

Para conservar un ensayo anterior, elegir otro proyecto aislado con el prefijo
`cermed-upgrade-` y usar el mismo nombre en ambos comandos:

```bash
CERMED_REHEARSAL_PROJECT=cermed-upgrade-real-20261024-verified \
  bash scripts/rehearse-mysql-upgrade.sh /ruta/privada/pre-upgrade.sql
make CERMED_REHEARSAL_PROJECT=cermed-upgrade-real-20261024-verified upgrade-check
```

El script exige esquemas vacíos. Restaura sucesivamente en 5.7, 8.0 y 8.4, detiene
cada motor antes del siguiente y compara tablas, conteos exactos, hashes de filas
y resultados de las vistas. Comprueba que exista un conteo por cada tabla y vista.
Imprime la carpeta privada con dumps, informes y logs de importación; estos últimos
pueden contener datos privados si una sentencia falla. Los eventos
MySQL quedan desactivados durante el ensayo. Un error de importación o diferencia
detiene el proceso y apaga el motor activo; no suprimirlo para continuar.

Ejecutar `upgrade-check` **después** de la restauración; si se ejecuta antes,
crea tablas y el ensayo se negará a sobrescribirlas. Para repetir un ensayo,
conservar primero sus informes y comprobar los volúmenes del proyecto aislado.
Solo entonces eliminar sus volúmenes desechables:

```bash
docker compose --project-name cermed-upgrade --env-file /dev/null \
  -f docker-compose-upgrade.yaml --profile legacy --profile intermediate down --volumes
```

No ejecutar ese comando con el Compose de producción. Los tests usan otra base
temporal; las migraciones de `upgrade-check` sí afectan a la copia de ensayo.
La comparación no sustituye la revisión de vistas, rutinas, definers, usuarios,
collations o permisos específicos de la base real. Revisar también el resultado
del Upgrade Checker de MySQL Shell para cada salto antes del corte.

**Cierre:** restauración real sin errores, comparaciones idénticas, tests pasando,
migraciones sin drift, estáticos, login/roles y recorridos de agenda/pagos/exportes
validados sobre la copia. Medir memoria, disco y duración de la restauración.

## 4. Validar dependencias e imágenes

```bash
pip-audit --disable-pip --no-deps -r requirements-prod.txt
docker build -t cermed-upgrade-nginx:local -f Dockerfile.nginx .
docker build -t cermed-upgrade-mysql:local -f Dockerfile.mysql .
bash scripts/scan-upgrade-images.sh /tmp/cermed-image-scans \
  cermed-upgrade-web:local cermed-upgrade-nginx:local \
  cermed-upgrade-mysql:local
```

Ejecutar `pip-audit` en el entorno de desarrollo instalado con el lock nuevo.
El modo mostrado devuelve error ante High/Critical y conserva los informes de
las imágenes y del Expat integrado. CI añade `--accept-reviewed-risk` antes del
directorio para evaluar la aceptación específica del 31/10: conserva los matches
y bloquea cualquier hallazgo fuera de esa política. No usa `--only-fixed`.
Los falsos positivos/componentes ausentes siguen en `config/grype.yaml`; sus
matches quedan en `ignoredMatches`. CI publica todos los JSON como artefactos.

Los hallazgos de un paquete de origen pueden afectar solo a ciertos binarios o
configuraciones. Deben contrastarse con el proveedor; un resultado del scanner
no prueba que exista una ruta explotable en CERMED. Tampoco se descarta sin evidencia.
El resumen local está en [UPGRADE-VALIDATION.md](UPGRADE-VALIDATION.md).

**Cierre:** resolver los hallazgos bloqueantes, o documentar y aprobar por separado
una excepción específica con evidencia. Las correcciones de falsos positivos
no aceptan riesgos de las vulnerabilidades que siguen pendientes.

## 5. Parches del host en una ventana separada

**Comprobado el 24/10/2026 a las 23:15 UTC:** APT no ofrece actualizaciones tras
refrescar los índices; no hay paquetes retenidos, unidades fallidas ni aviso de
reinicio. No hace falta ejecutar `apt upgrade` o reiniciar con este resultado.
La revisión se repetirá si la ventana de despliegue se realiza otro día.

Para repetir la revisión del droplet, el bloque está en
[DROPLET-HOST-CHECKS.txt](DROPLET-HOST-CHECKS.txt). Actualiza índices APT y simula
la instalación; no instala paquetes ni reinicia servicios.

Antes de cambiar Ubuntu/Docker, obtener snapshot y backups comprobados. Revisar:

```bash
sudo apt-get update
apt list --upgradable
sudo apt-get -s upgrade
systemctl --failed
test ! -f /var/run/reboot-required || cat /var/run/reboot-required
```

`apt-get update` actualiza índices; la simulación no instala paquetes. Revisar
qué servicios se reiniciarán, aplicar los parches aprobados de Ubuntu 22.04 y
revalidar servicios/HTTP. No combinar un cambio de release Ubuntu con el corte de
MySQL. Si hace falta reiniciar el host, hacerlo en la ventana acordada.

## 6. Corte de producción y reversión

### Preparar TLS de MySQL

Antes de arrancar los contenedores nuevos, generar certificados **fuera del repo**.
Usar una copia revisada de `scripts/create-mysql-tls.sh` fuera del checkout servido;
no hacer `git pull` en el checkout vivo para obtenerla. Este ejemplo lee solo el
hostname de la aplicación actual; no imprime contraseñas ni modifica servicios:

```bash
cermed_mysql_host=$(docker exec cermed_web python -c 'import os; print(os.environ["MYSQL_HOST"])')
cermed_tls_dir="$HOME/cermed-mysql-tls/$(date -u +%Y%m%dT%H%M%SZ)"
bash /ruta/a/create-mysql-tls.sh "$cermed_tls_dir" "$cermed_mysql_host" db cermed_db localhost 127.0.0.1 cermed.com.ar 142.93.11.29
printf 'CERMED_MYSQL_TLS_DIR=%s\n' "$cermed_tls_dir"
```

Guardar la línea resultante en `.env.prod`. En desarrollo, ejecutar el mismo
generador con el `MYSQL_HOST` de `.env` y guardar allí `CERMED_MYSQL_TLS_DIR` antes
de `make run`. Compose monta `server/` solo en MySQL y `client/` solo en web,
siempre en lectura; no crea directorios ausentes. Nunca montar `authority/`.
El directorio exterior es 0700 y la clave CA es 0600. La clave del servidor es
legible por el UID de MySQL dentro de su montaje; permanece protegida en el host
por el directorio exterior. Respaldar la carpeta por un canal privado.

El certificado dura un año. Revisar su vencimiento en el mantenimiento mensual:

```bash
openssl x509 -in "$cermed_tls_dir/server/server-cert.pem" -noout -enddate -checkend 2592000
```

Un resultado no cero requiere renovar antes de 30 días: generar otra carpeta,
actualizar `CERMED_MYSQL_TLS_DIR` y recrear db/web en una ventana de mantenimiento.
El generador crea una CA nueva; actualizar también la confianza de DBeaver.
No sobrescribe material existente. No usar una renovación HTTPS de Certbot para
estos certificados internos.

Para DBeaver, conectar directamente a `cermed.com.ar:3308` o `142.93.11.29:3308`,
con SSH deshabilitado, base `gym_db` y las credenciales habituales. Habilitar TLS
con `client/ca.pem` como CA y verificación de identidad (`sslMode=VERIFY_IDENTITY`
en el driver MySQL). El certificado debe incluir el dominio y la IP pública en
su SAN; el certificado inicial del corte solo incluía los destinos internos.
El administrador puede entregar al analista únicamente el certificado público
`client/ca.pem`; el analista no necesita una cuenta SSH. No copiar claves privadas
al cliente ni desactivar la verificación. Comprobar lectura y escritura durante la
ventana. MySQL rechazará conexiones TCP sin cifrar; las conexiones locales por
socket utilizadas para mantenimiento siguen disponibles.

### Ejecutar el corte

Esta etapa se prepara con los resultados reales anteriores; todavía no se ejecutó.
Antes del corte, ejecutar [DROPLET-PREDEPLOY-CHECKS.txt](DROPLET-PREDEPLOY-CHECKS.txt)
para comprobar TLS, vigencia, cron y presencia de hooks personalizados. No instala
ni renueva certificados. Cualquier hook que necesite curl o módulos retirados
debe revisarse antes de adoptar la imagen reducida.
El checkout actual está montado dentro del contenedor web: **un `git pull` ya
cambia código servido**, aun sin reconstruir la imagen. Congelar escrituras antes
de actualizar ese checkout y conservar el commit, imágenes, Compose y configuración
anteriores fuera de él para poder volver.

1. Anunciar mantenimiento; detener web y su cron, escritores externos y sesiones
   DBeaver con capacidad de escritura. Bloquear nuevas operaciones durante el corte.
2. Tomar el backup final y verificarlo. Conservar intacto el volumen 5.7, detenido.
3. Restaurar en volúmenes nuevos, primero 8.0 y luego 8.4. Mantener el nombre real de
   la base y recrear usuarios/permisos compatibles, sin importar tablas internas
   de MySQL 5.7. Comparar nuevamente conteos y contenido. No usar en producción
   el volumen de ensayo con credenciales `rehearsal-only`.
4. En `.env.prod`, fijar `CERMED_MYSQL84_VOLUME` al volumen 8.4 **ya restaurado y
   validado**, y `CERMED_MYSQL_TLS_DIR` a los certificados preparados. Compose
   exige ambos; nunca apuntar al volumen 5.7.
5. Actualizar el checkout y construir las imágenes aprobadas. Validar con
   `docker compose --env-file .env.prod -f docker-compose-prod.yaml config --quiet`.
   No compartir `config` sin `--quiet`: expone valores resueltos del entorno.
6. Levantar aplicación/proxy; revisar migraciones, estáticos, `check --deploy`,
   login, roles, pacientes, agendas, cuotas/pagos, PDF/XLSX y acceso de medios.
   Verificar cron y renovación de certificados, sin duplicar tareas.
7. Generar un backup nuevo de 8.4 y restaurarlo en un entorno aparte; comparar
   contenido. Solo después reabrir escrituras y registrar la hora del corte.
8. Habilitar la variable de repositorio Actions `CERMED_MYSQL84_READY=true` cuando
   la migración esté aprobada. Hasta entonces el job de deploy queda deshabilitado,
   aunque CI pase. El despliegue sigue usando SSH + git/Compose.

Antes de reabrir escrituras, revertir significa detener los servicios nuevos y
restaurar el checkout, imagen, configuración y volumen 5.7 anteriores. No conectar
MySQL 5.7 al volumen 8.4. Después de reabrir escrituras, volver a la copia anterior
perdería operaciones nuevas: detenerse y preparar reconciliación/recuperación.

**Cierre:** smoke aprobado, backup 8.4 restaurable, reapertura registrada y recursos
estables. Conservar los backups y el volumen anterior durante el plazo acordado.

## 7. Seguimiento

Revisar durante el siguiente día hábil errores 5xx, logs de aplicación/Nginx/MySQL,
memoria/swap/OOM, espacio, tiempos de respuesta, cron y backup nocturno. Registrar
las advertencias existentes de `check --deploy`; HTTPS/cookies/headers requieren
una etapa de configuración separada, fuera del alcance acordado de versiones.

## Fuentes

- [Ruta oficial MySQL 5.7 → 8.0 → 8.4](https://dev.mysql.com/doc/refman/8.4/en/upgrade-paths.html).
- [Imágenes oficiales Python](https://hub.docker.com/_/python).
- [Avisos Nginx](https://nginx.org/en/security_advisories.html): 1.31.6 está dentro
  de los rangos afectados por avisos corregidos en 1.31.7+/1.30.6+. Se elige
  [1.31.8](https://nginx.org/en/CHANGES) para conservar la rama de producción.
  La exposición de cada aviso depende de la configuración; no se probó explotación.
- [Checklist de despliegue Django 5.2](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
