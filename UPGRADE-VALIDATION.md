# Evidencia local — 24/10/2026

**Restauración real y validaciones automáticas locales: aprobadas. Seguridad de
imágenes: bloqueada. Actualización de versiones en producción: pendiente.** El
usuario aplicó únicamente la corrección puntual del cron de certificados y validó
ACME staging. No se desplegaron las nuevas dependencias ni se cambiaron datos de
la aplicación. La validación previa al commit se detalla al final.

| Validación | Resultado |
| --- | --- |
| Baseline Django 4.1 / MySQL 5.7 | 52 tests pasan; corregidas dos expectativas/fixtures obsoletas |
| Python 3.12.15 / Django 5.2.18 / MySQL 8.4.13 | 59 tests pasan |
| `pip check` | Sin incompatibilidades, runtime y desarrollo |
| Lock producción, 23 paquetes | `pip-audit`: sin vulnerabilidades conocidas |
| Lock desarrollo, 80 paquetes | `pip-audit`: sin vulnerabilidades conocidas |
| Build de producción/desarrollo/Nginx | Correcto; instalación Python con hashes |
| `check`, migraciones y drift | Sin errores ni cambios de modelos; advertencia URL indicada abajo |
| `collectstatic --dry-run` | 134 archivos; sin errores |
| MySQL 5.7 → 8.0 → 8.4 | Backup real: 62 tablas, 91.098 filas y 2 vistas; conteos y hashes idénticos |
| Upgrade Checker oficial, Shell 26.7.1 | Cero errores en ambos saltos sobre la copia real; advertencias de defaults/autenticación detalladas abajo |
| Copia externa del backup real | Checksum verificado independientemente desde la computadora local |
| Django sobre la copia real | Sin migraciones pendientes ni drift; 59 tests pasan en su base temporal separada |
| Backup y restauración con django-dbbackup 5.4 | Datos reales: mismo hash completo, 62 conteos y resultados de ambas vistas después de restaurar |
| Gunicorn, 2 workers × 4 threads | HTTP 200 en login y admin; formularios CSRF presentes |
| Nginx reducido y Certbot | `cermed.conf` con TLS temporal: redirect, proxy/login/CSRF, estáticos, medios, ACME webroot, config/reload y cron pasan |
| Configuración TLS real del droplet, 25/10 02:26 UTC | `nginx -t` pasa; login HTTP 200 y TLS_verify=0; certificado válido hasta 14/12/2026 |
| Renovación del droplet | Invocación reparada en cron y entrypoint persistente; simulación ACME staging exitosa; HTTPS posterior 200/TLS_verify=0 |
| Scripts y Compose aislado | Sintaxis y `config --quiet` correctos |
| Host Ubuntu, 24/10/2026 23:15 UTC | Índices APT actualizados; simulación 0 upgrades, sin paquetes retenidos, servicios fallidos ni aviso de reinicio |
| Aceptación funcional local | Usuario informó que parece funcionar bien; aceptación general, sin resultados detallados por pantalla/rol |

Los tests cubren consultas existentes, PDF, XLSX, compatibilidad de formatos,
ubicación de backups, login con hash de contraseña anterior, preservación de rol
y rechazo de usuarios inactivos/sin área. No sustituyen la aceptación manual de
agendas y pagos con datos reales ni una prueba de carga del droplet.

## Escaneo de imágenes

Grype 0.121.0, base de vulnerabilidades del 24/10/2026. Se escaneó la imagen
construida, incluyendo paquetes del sistema y Python. La tabla conserva los
resultados brutos, sin exclusiones, con umbral `--fail-on high`.

| Imagen | High | Critical | Identificadores únicos High/Critical |
| --- | ---: | ---: | ---: |
| Web: Python 3.12.15 slim Bookworm + paquetes actualizados | 116 | 13 | 33 |
| Nginx 1.31.8 + cron/certbot, sin módulos opcionales ni curl | 77 | 4 | 25 |
| MySQL 8.4.13 derivada: certificados actualizados y sin MySQL Shell | 5 | 0 | 3 |

Los conteos son coincidencias paquete/aviso: una vulnerabilidad puede aparecer
en varios paquetes. No equivalen a ese número de rutas explotables. En las dos
imágenes Debian, Grype no ofrece versiones corregidas para esos High/Critical
en la distribución seleccionada. La imagen oficial MySQL tenía 14 High y 2 Critical.
Se corrigió el almacén de certificados y se retiró MySQL Shell, herramienta auxiliar
con librerías Python antiguas. Las cinco coincidencias restantes sobre tres
avisos OpenSSL/GnuTLS se confirmaron como cruces incorrectos contra variantes
FIPS: los RPM no FIPS instalados ya incluyen las correcciones de Oracle.
`config/grype.yaml` limita cada exclusión al aviso, distribución, paquete y
versión exactos; siguen visibles en `ignoredMatches`. Con esas reglas, MySQL
pasa (0 High/Critical pendientes).

La revisión posterior confirmó ocho CVE MariaDB ya corregidos en el cliente
10.11.19 instalado. Las reglas exactas para Debian 12 conservan 32 coincidencias
en `ignoredMatches`; web queda en **92 High / 5 Critical** pendientes, sin
alterar los demás matches. Nginx retiró 66 paquetes no usados; bajó de 113/18
a **77 High / 4 Critical**, sin exclusiones adicionales. Ambos siguen bloqueando
CI. Ver [UPGRADE-IMAGE-TRIAGE.md](UPGRADE-IMAGE-TRIAGE.md).

Los JSON completos quedan localmente en `/tmp/cermed-final-scans/image-{1,2,3}.json`.
El informe 2 corresponde al primer ensayo con Nginx 1.30.6. Después de recibir
el inventario real (Nginx 1.31.6), se conservó su rama y se actualizó a 1.31.8;
build, `nginx -t` por defecto y Certbot pasan. El nuevo escaneo está en
`/tmp/cermed-nginx-1318-scan/image-1.json`, previo a retirar módulos opcionales.
La imagen reducida actual se escaneó en `/tmp/cermed-nginx-reduced-scan/image-1.json`;
estos son los conteos Nginx de la tabla. El informe web con las reglas MariaDB
está en `/tmp/cermed-web-reviewed-scan/image-1.json`.
El informe 3 inicial era de MySQL oficial. El nuevo, después de aplicar
`Dockerfile.mysql`, está en `/tmp/cermed-mysql-runtime-scan/image-1.json`.
Son archivos temporales: CI los vuelve a generar y publica como artefactos. El
comando reproducible está en `UPGRADE-2026.md`. Esta barrera de CI **fallará con
estos resultados**; activar la variable de deploy no evita el fallo de CI.

La base web se redujo de la imagen completa a slim, con compiladores separados.
Se conserva Bookworm con parches: el cliente MariaDB de Trixie cambió la
verificación de certificados y rompió el backup contra la configuración actual.
No se desactivó TLS para sortear ese error. El backup/restauración se comprobó
de nuevo con el cliente compatible de Bookworm.

La imagen Nginx reducida pasó un smoke con `cermed.conf` y certificados locales
temporales, sin usar claves productivas. Se corrigió cron para invocar mediante
`/bin/sh` el script de renovación guardado sin bit ejecutable en Git. Se verificó
el flujo del script en el entorno sin certificados renovables; esto no demuestra
una renovación ACME real. El usuario completó
[DROPLET-PREDEPLOY-CHECKS.txt](DROPLET-PREDEPLOY-CHECKS.txt) el 25/10 a las 02:26 UTC:
webroot confirmado, sin hooks en la configuración del certificado ni archivos
en los tres directorios de hooks. Cron estaba activo, pero el script 664 se invocaba
sin sh, confirmando el fallo en el servidor. El certificado RSA de cermed.com.ar
vence el 14/12/2026 a las 14:20:34 UTC y HTTPS funciona.

El usuario ejecutó [DROPLET-FIX-CERTBOT-CRON.txt](DROPLET-FIX-CERTBOT-CRON.txt)
correctamente. Se respaldaron entrypoint (522 bytes) y cron (83 bytes) en
`/home/cermed/cermed-upgrade-backups/cron-fix.j10B9dAV/`. Ambos invocan ahora el
script mediante `/bin/sh`; cron conserva modo 644 y `nginx -t` pasa. Certbot
informó que la renovación simulada de cermed.com.ar fue exitosa. La comprobación
posterior devolvió HTTP 200 y TLS_verify=0; el certificado productivo no se
reemplazó. No se reiniciaron servicios ni se desplegó la actualización general.

El cambio del entrypoint queda en el checkout montado del servidor: conservarlo
al preparar el futuro despliegue. Se validó el camino manual de renovación y
se reparó la invocación; todavía no se observó una ejecución futura por horario.

Recursos productivos medidos: 334 MiB disponibles, 73 MiB de swap usados y 9.7 GiB
libres; contenedores web 234.6 MiB, MySQL 5.7 86 MiB, Nginx 15.3 MiB. Esta muestra
del stack anterior no demuestra capacidad suficiente para MySQL 8.4 bajo carga.

## Advertencias y límites

- `urls.W010`: ruta preexistente `<error_profesional_existente/` con un `<` sin
  pareja. No se alteró esa URL pública en una actualización de dependencias.
- `check --deploy` informa W004/W006/W008/W012/W016 en el entorno de ensayo:
  HSTS, nosniff, redirect HTTPS y cookies seguras. Revisar los valores reales del
  servidor; los cambios de endurecimiento se acordaron para otra etapa.
- Se ensayó el backup real en Docker local y el usuario aceptó la prueba funcional.
  Siguen pendientes la ventana de mantenimiento y el rollback del droplet.
  El Upgrade Checker local no valida usuarios ni configuración reales del servidor.
  No se comprobó el backup nocturno. La invocación del cron de certificados se
  reparó y ACME staging pasó; falta observar su próxima ejecución programada.
  La RAM de 957 MiB requiere validar el stack actualizado allí.
- El resultado de `pip-audit` es puntual y no cubre por sí solo la imagen, el host,
  recursos estáticos de terceros ni evidencias de compromiso.

## Evidencia de archivos e imágenes

- Pruebas: `/tmp/cermed-upgrade-check-final.log`.
- Auditoría de locks: `/tmp/cermed-locks-audit.log`.
- Backup/restauración real: `/tmp/cermed-real-backup-roundtrip.log`.
- Validaciones Django del ensayo real: `/tmp/cermed-real-django-check.log`.
- Ensayo real corregido: `/tmp/cermed-real-rehearsal-verified.log` y
  `/tmp/cermed-mysql-rehearsal.CGrhYe/` (privados).
- Hash de filas después del nuevo backup/restauración:
  `/tmp/cermed-real-roundtrip.rows.sha256`.
- Inventario del runtime: `/tmp/cermed-final-runtime.json`.
- Los archivos temporales son evidencia de esta ejecución, no entradas del build.

El inventario inicial del droplet ya fue recibido: Python 3.10.21, Django 4.1.12,
MySQL 5.7.44, Nginx 1.31.6, Docker 29.9.2, Compose v5.6.1 y directorio MySQL de
248 MB. El usuario ya ejecutó [DROPLET-HOST-CHECKS.txt](DROPLET-HOST-CHECKS.txt):
no hay actualizaciones APT pendientes en los repositorios configurados. Kernel
`5.15.0-198-generic`, 300 MiB de RAM disponible, 73 MiB de swap usada y 9.7 GiB
libres. No se necesita instalar paquetes ni reiniciar por este resultado.
Esto no actualiza los paquetes dentro de las imágenes. El siguiente trabajo es
resolver sus hallazgos y completar la aceptación previa al corte. Seguir
[UPGRADE-2026.md](UPGRADE-2026.md), sin saltar los criterios de cierre.

La imagen MySQL derivada también pasó inicialización limpia, restauración del
dump real 8.4, los 59 tests/checks y generación/restauración de un nuevo backup,
con hash completo de datos idéntico. Logs: `/tmp/cermed-mysql-patched-check.log`,
`/tmp/cermed-mysql-patched-backup.log` y `/tmp/cermed-mysql-patched-restored.rows.sha256`.
Se dejó una copia local en `http://127.0.0.1:18000/usuarios/login/` para la
[aceptación funcional](LOCAL-ACCEPTANCE.md). Las modificaciones manuales posteriores
afectarán esa copia; los hashes documentados corresponden al estado anterior.

## Backup real confirmado por el usuario

- Carpeta del droplet: `/home/cermed/cermed-upgrade-backups/20261024T230006Z.nK5kPg`.
- Tamaño de `pre-upgrade.sql`: 4.789.350 bytes; 62 tablas InnoDB.
- SHA-256: `e643f0209d8e7791e12753d32cd10f0460b07120cf777c76d24f6ef0e0c9a2de`.
- Volumen original: `gym_django_db_data`; conservarlo para la reversión.
- Imagen web: `sha256:a09bf45ed7d492ba8cba6ab75f3b1ddf3ed2648a49fa30f722a281a0364f8d28`.
- Imagen MySQL: `sha256:5107333e08a87b836d48ff7528b1e84b9c86781cc9f1748bbc1b8c42a870d933`.
- Imagen Nginx: `sha256:7d383c7e5010efdb97ea55a0258a6e09d7abbc83c2c6b81209709bbbca385cbf`.

La copia se verificó en
`/home/alfonso/cermed-upgrade-backups/received.cKyuNu/20261024T230006Z.nK5kPg/`.
El ensayo final usó el proyecto aislado `cermed-upgrade-real-20261024-verified`,
con volúmenes nuevos, red interna y sin puertos publicados. El proyecto
`cermed-upgrade-real-20261024` sirvió para checks de Django y el backup/restauración
de 8.4. El original y los ensayos anteriores se conservaron.

Se detectó y corrigió un defecto del validador: `docker exec` consumía la entrada
del bucle y solo generaba el conteo de la primera tabla. Los hashes completos
anteriores coincidían, pero ese informe de conteos era incompleto. Se repitió
desde cero el ensayo real tras redirigir stdin y agregar una comprobación de
cobertura: los tres informes finales contienen 62 conteos y 2 resultados de vistas.
Las dos vistas se consultan sin error y conservan sus resultados; no hay rutinas,
triggers ni eventos en este esquema. Hay 91.098 filas entre todas las tablas,
incluyendo tablas internas de Django; no es un conteo de pacientes.

Este dump sirve para el ensayo. Se necesitará otro con las escrituras detenidas
durante el corte definitivo.

## Upgrade Checker oficial sobre la copia restaurada

Se ejecutó MySQL Shell 26.7.1 en un contenedor auxiliar de la red interna del
proyecto `cermed-upgrade-real-20261024-verified`, sin puertos publicados.
La distribución Linux generic se obtuvo del CDN oficial de MySQL y su firma
GPG se verificó con la clave de Oracle obtenida por HTTPS, fingerprint
`BCA43417C3B485DD128EC6D4B7B3B788A8D3785C`.

| Origen → destino solicitado | Checks ejecutados | Errores | Advertencias | Avisos |
| --- | ---: | ---: | ---: | ---: |
| 5.7.44 → 8.0.46 | 32, todos ejecutados correctamente | 0 | 64 | 1 |
| 8.0.46 → 8.4.13 | 11, todos ejecutados correctamente | 0 | 24 | 2 |

Las advertencias corresponden a defaults que cambian, autenticación
`mysql_native_password` de cuentas del ensayo y privilegios retirados. El aviso
de 5.7 señala `NO_AUTO_CREATE_USER`. No aparecieron incompatibilidades del
esquema. La estrategia sigue siendo restauración lógica en instancias nuevas:
no trasladar las tablas internas de usuarios ni el archivo de configuración 5.7.
Crear usuarios compatibles con `caching_sha2_password` y comprobar las conexiones
de Django, backup y DBeaver antes de abrir escrituras. Los dos primeros ya se
probaron localmente; DBeaver y los permisos reales siguen pendientes.

El checker recibió los `my.cnf` locales más las opciones de Compose del ensayo;
los directorios incluidos estaban vacíos. No inspeccionó configuración, cuentas
ni grants del droplet. Los cambios de defaults de memoria, temporales y redo
requieren la medición prevista en el host de 957 MiB: estos resultados no son
una prueba de capacidad. Se detuvieron ambos contenedores de etapa al terminar.

Informes privados: `/tmp/cermed-upgrade-checker/mysql57-to80.json` y
`/tmp/cermed-upgrade-checker/mysql80-to84.json`. Invocación usada, cambiando
host/target/config para cada etapa:

```javascript
util.checkForServerUpgrade(
  {user: "root", password: "rehearsal-only", host: "db80", port: 3306},
  {targetVersion: "8.4.13", configPath: "/checks/mysql80.cnf", outputFormat: "JSON"}
)
```

Usar `mysqlsh --no-defaults --js` para no heredar el socket `[client]` de la imagen
auxiliar. La contraseña mostrada solo pertenece al entorno desechable. Consultar
el [manual del Upgrade Checker](https://dev.mysql.com/doc/mysql-shell/26.7/en/mysql-shell-utilities-upgrade.html).

## Validación previa al commit — 25/10/2026

Se reconstruyeron las imágenes web y MySQL desde el checkout actual. Se ejecutó
`scripts/validate-upgrade.sh` mediante Compose en el proyecto aislado
`cermed-upgrade-precommit-20261025`, con un volumen MySQL 8.4 nuevo y sin puertos
publicados. La copia de aceptación y producción no se modificaron.

- Suite completa de las seis apps: **59 tests, 2.634 segundos, OK**.
- `pip check`, chequeos Django, migración desde cero y comprobación de migraciones
  pendientes: sin errores. `makemigrations --check --dry-run`: sin cambios.
- `collectstatic --dry-run --noinput`: 134 archivos.
- `check --deploy`: las cinco advertencias de seguridad y `urls.W010` ya descritas.
- Sintaxis de scripts/Python, YAML, Compose aislado y `git diff --check`: correctos.
- Se revisaron los 48 archivos seleccionados: sin dumps, archivos de entorno,
  medios, estáticos generados ni coincidencias con patrones de claves privadas/tokens.

Log: `/tmp/cermed-precommit-validation.log`. Se detuvo el contenedor de base
temporal después de validar. Este resultado no convierte en aprobado el control
de imágenes: sus hallazgos y el despliegue productivo siguen pendientes.
