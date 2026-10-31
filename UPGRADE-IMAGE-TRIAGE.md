# Revisión de avisos de imágenes — 24/10/2026

## Candidata web Trixie — 31/10/2026, TLS y backups validados localmente

Se ensayó Python 3.12.16 sobre Trixie, con glibc `2.41-12+deb13u4`
y OpenSSL `3.5.7-1~deb13u3`. El CVE-2026-5450 desaparece del escaneo
sin filtro: [Debian confirma la corrección en Trixie](https://security-tracker.debian.org/tracker/CVE-2026-5450).
Los clientes MariaDB provienen del archivo oficial firmado 11.8.9 para Trixie,
versión `1:11.8.9+maria~deb13`; Connector/C cargado por mysqlclient es `3.4.10`.
La clave se verificó con la [huella oficial](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/installing-mariadb/binary-packages/gpg)
`177F4010FE56CA3336300305F1656F24C74CD1D8`; el Dockerfile fija su SHA-256
y APT limita esa clave al repositorio de MariaDB.

La [tabla oficial de MariaDB 11.8](https://mariadb.com/docs/release-notes/community-server/11.8/what-is-mariadb-118.md)
confirma los 14 avisos filtrados: 44168/44171/44172 en 11.8.7,
48163/48165/49261 en 11.8.8 y los ocho ya revisados en 11.8.9 (todos CVE-2026).
Grype los sigue asociando a la información de Debian 11.8.6. Las reglas cubren
únicamente esa versión upstream y los seis paquetes cliente enumerados;
`check-image-exceptions.sh` comprueba versiones, Connector/C y ausencia de servidor.
Se retiraron las reglas Bookworm que ya no corresponden a las imágenes propuestas.

Resultado web: **63 High / 0 Critical**, con 84 coincidencias MariaDB corregidas
conservadas en `ignoredMatches`; ninguna otra coincidencia se retiró respecto del
escaneo de la misma candidata sin esas reglas. CI sigue bloqueando por High.
Pasaron los 59 tests, migraciones y simulación de 134 estáticos en MySQL 8.4 aislado.
Los checks mantienen los warnings de URL existente y de HTTPS en el entorno de ensayo.

El ensayo inicial reprodujo un fallo de `dbbackup`: MariaDB 11.8 rechaza el
certificado autofirmado predeterminado de MySQL. Se resolvió configurando una CA
privada y certificado con SAN, compartiendo solo la CA pública con web. Django
verifica identidad y los clientes CLI verifican el certificado; MySQL exige TLS
en TCP. No se desactivó la verificación para conservar los backups.

`check-mysql-client.sh` pasó backup/restauración con Unicode, binarios, decimales,
fechas, NULL y una vista; luego los 59 tests sobre TLS. Usa un usuario limitado a
la base sintética y su base de tests, sin privilegios globales. Tanto ORM como CLI
rechazan host incorrecto, CA incorrecta y CA ausente; MySQL rechaza TCP sin TLS.
Las imágenes de producción y desarrollo construyen. Se mantiene el warning de URL
ya existente. El generador rechaza sobrescritura y claves dentro del repositorio.

**Producción sigue pendiente:** deben prepararse los certificados y resolver los
avisos High; no se hizo push ni despliegue en esta etapa. Preparación y renovación
en `UPGRADE-2026.md`. Evidencia final: `/tmp/cermed-trixie-tls-scan/image-1.json`,
`/tmp/cermed-trixie-tls-appuser-check.log`; reproducción anterior:
`/tmp/cermed-trixie-mariadb-backup.log`.

## Actualización validada el 27/10/2026

Se incorporaron OpenSSL `3.0.22-1~deb12u2`, Brotli `1.0.9-10.0.1.el9_8`
y Certbot `5.8.0` en un venv con hashes, cryptography `50.0.2` y urllib3 `2.8.0`.
Cron usa rutas absolutas y detiene la recarga si falla la renovación o `nginx -t`.
Los locks de producción/Certbot pasaron pip-audit; pasaron 59 tests, migraciones,
134 estáticos y backup/restauración en una base desechable. El smoke de Nginx
verificó TLS temporal, proxy, archivos, webroot y cron, incluyendo fallo sin
recarga. La renovación ACME real con esta imagen sigue pendiente.

Ocho reglas nuevas en `config/grype.yaml` conservan los matches ignorados y se
limitan al aviso, distribución, paquete y versión. Su evidencia es:

- [ACL CVE-2026-54370](https://security-tracker.debian.org/tracker/CVE-2026-54370):
  `getfacl`, `setfacl` y `chacl` ausentes en web y Nginx; el aviso de biblioteca
  CVE-2026-54369 permanece visible.
- Perl [CVE-2026-82560](https://security-tracker.debian.org/tracker/CVE-2026-82560)
  y [CVE-2026-9538](https://security-tracker.debian.org/tracker/CVE-2026-9538):
  `Pod::Text` y `Archive::Tar` ausentes solo en Nginx, comprobados por import.
- SQLite [CVE-2025-7458](https://security-tracker.debian.org/tracker/CVE-2025-7458),
  [CVE-2026-11822](https://security-tracker.debian.org/tracker/CVE-2026-11822) y
  [CVE-2026-11824](https://security-tracker.debian.org/tracker/CVE-2026-11824):
  producción usa MySQL; no ejecuta SQL arbitrario en SQLite ni ingiere bases SQLite.
- [Python CVE-2026-19445](https://security-tracker.debian.org/tracker/CVE-2026-19445):
  TLS termina en Nginx, sin servidor Python con sustitución de contexto SNI.
  Certbot usa webroot; el droplet reportó ausencia de hooks personalizados.

`check-image-exceptions.sh` verifica componentes ausentes y backend MySQL en CI.
Reevaluar al cambiar motores, carga de bases, terminación TLS, plugins o hooks.
Estas condiciones no convierten las bibliotecas en versiones parcheadas.

Resultado del 27/10: web **87 High / 4 Critical**, Nginx **70 High / 0 Critical**,
MySQL **0 High / 0 Critical**. Las cuatro críticas restantes son CVE-2026-5450
(glibc). **CI conserva el bloqueo por High; no se aprobó ni implementó una
excepción temporal para el riesgo residual.** Los conteos siguientes son
históricos. No hubo despliegue productivo durante estas validaciones.

## Evidencia histórica del 24/10

**Estado: revisión parcial priorizada; CI sigue bloqueado.** Este documento
clasifica evidencia y documenta exclusiones específicas por falsos positivos
confirmados de Oracle y MariaDB. No acepta riesgos sobre los demás hallazgos.
Que APT no tenga pendientes en Ubuntu no actualiza las imágenes Debian/Oracle.

## Corrección implementada en MySQL

La imagen oficial de MySQL 8.4.13 incluía `ca-certificates` de 2025 y MySQL Shell
8.4.10 con sus propias dependencias Python. El scanner ubicó certifi, cryptography,
pyOpenSSL y urllib3 bajo `/usr/lib/mysqlsh/lib/python3.13/site-packages/`.

`Dockerfile.mysql` actualiza los certificados desde Oracle y retira `mysql-shell`.
El proyecto y el entrypoint oficial no lo usan para servir la base o hacer backups;
`mysqld`, `mysql` y `mysqldump` permanecen en 8.4.13. El Upgrade Checker debe
ejecutarse por separado. La actualización de certificados está respaldada por
el [aviso de Oracle sobre eMudhra](https://linux.oracle.com/errata/ELSA-2026-500450.html).
La construcción instaló `ca-certificates-2026.2.92_v9.0.319-90.3.el9_8`.

El ensayo que solo ejecutaba `microdnf upgrade` actualizó los certificados, pero
dejó Shell y sus librerías antiguas. Por eso no bastaba con actualizar paquetes
del sistema. No se sustituyeron manualmente librerías dentro del bundle de Shell.

## Hallazgos revisados y límites de la conclusión

### Reducción validada de la imagen Nginx

Se retiraron `curl` y los módulos opcionales `acme`, `geoip`, `image-filter`,
`njs` y `xslt`, que no están cargados en la configuración del proyecto. APT
retiró también sus dependencias: 66 paquetes en total, incluidos libcurl,
libxml2, libtiff y códecs gráficos. Se conservan Nginx, cron y Certbot webroot.
El healthcheck SSH usa curl del host; no depende de curl dentro de esta imagen.

Grype pasó de **113 High / 18 Critical a 77 High / 4 Critical**, sin agregar
exclusiones para Nginx. Los identificadores únicos High/Critical bajaron de 53
a 25. Las cuatro coincidencias Critical restantes son el mismo aviso Python
CVE-2026-19445, asociado a cuatro paquetes binarios.

La prueba utilizó `cermed.conf` real con certificado temporal verificado y una
copia local de Django: redirección HTTP, TLS, login con CSRF, estáticos, medios,
ACME webroot, `nginx -t`, reload, plugin Certbot webroot y cron pasan. No se
emitió ni renovó un certificado real en esa prueba local. Posteriormente el
usuario verificó los hooks del droplet y completó una renovación ACME staging
exitosa con la imagen productiva actual; la imagen reducida sigue sin desplegarse.

También se corrigió la invocación de cron: `certbot-renewal.sh` está guardado
como 100644 en Git, por lo que ahora se ejecuta mediante `/bin/sh`. Esto evita
depender de un chmod manual del servidor. La inspección posterior del usuario
confirmó el mismo fallo en el droplet: script 664, cron activo e invocación sin sh.
TLS y webroot pasan; no se encontraron hooks en la configuración del certificado
ni en los directorios de hooks. El usuario ejecutó
[DROPLET-FIX-CERTBOT-CRON.txt](DROPLET-FIX-CERTBOT-CRON.txt): reparación del
entrypoint persistente y cron actual confirmada, simulación de renovación exitosa
y HTTPS posterior 200/TLS_verify=0. Respaldo:
`/home/cermed/cermed-upgrade-backups/cron-fix.j10B9dAV/`.

Logs: `/tmp/cermed-nginx-reduced-build.log`, `/tmp/cermed-nginx-reduced-smoke.log`
y `/tmp/cermed-nginx-reduced-scan/image-1.json`.

### Revisión por aviso

| Aviso / componente | Evidencia y disposición |
| --- | --- |
| CVE-2026-85746, MariaDB | La [fuente upstream](https://github.com/MariaDB/server/security/advisories/GHSA-8fvj-c57c-pggx) describe código GIS del servidor y marca 10.11.19 corregida. La imagen web usa clientes 10.11.19 y no contiene `mysqld`/`mariadbd`. No hay componente servidor afectado en esa imagen; Debian todavía lo asocia al paquete fuente. |
| CVE-2026-92262, MariaDB | El [aviso upstream](https://github.com/MariaDB/server/security/advisories/GHSA-65jj-h265-3m7h) afecta nombres de tablas en el servidor y también marca 10.11.19 corregida. Misma distinción entre paquete cliente y servidor. No se extendió esta conclusión a todos los CVE de MariaDB. |
| CVE-2026-52490, TIFF | [Debian](https://security-tracker.debian.org/tracker/CVE-2026-52490) ubica el fallo en `tools/tiffcrop.c`. `tiffcrop` no está instalado en la imagen Nginx; la coincidencia es contra `libtiff6`. Evidencia de componente afectado ausente para este aviso específico. |
| CVE-2026-19445, Python | [Debian](https://security-tracker.debian.org/tracker/CVE-2026-19445) exige un servidor TLS Python que cambie el contexto en un callback SNI; los clientes TLS no están afectados. El Python de Nginx se usa para Certbot con webroot; TLS entrante lo sirve Nginx. No se identificó ese flujo vulnerable en la configuración del repo. |
| CVE-2025-7458, SQLite | [Debian](https://security-tracker.debian.org/tracker/CVE-2025-7458) requiere ejecutar SQL arbitrario contra SQLite. Producción usa MySQL; `gym/gym/test_settings.py` sí usa SQLite para tests. No se encontró una entrada SQL externa hacia SQLite, pero la biblioteca sigue presente. No se clasifica toda SQLite como libre de riesgo. |
| CVE-2026-5450, glibc | [Debian](https://security-tracker.debian.org/tracker/CVE-2026-5450) describe un uso específico de `scanf` con `%mc` y ancho mayor a 1024; lo considera menor en Bookworm. La biblioteca afectada está presente. Falta demostrar la ausencia de esa llamada en dependencias nativas; queda pendiente. |
| CVE-2026-10536, curl | [Debian](https://security-tracker.debian.org/tracker/CVE-2026-10536) exige dependencias de streams HTTP/2 junto con reset/cleanup de handles. `ldd /usr/sbin/nginx` no muestra libcurl. Esto no prueba que ningún proceso auxiliar use libcurl: queda pendiente y no cubre otros avisos curl. |
| CVE-2026-6653, libxml2 | [Debian](https://security-tracker.debian.org/tracker/CVE-2026-6653) describe parsing de XML malicioso. No hay `load_module`, `xslt` ni `image_filter` en los `.conf` de la imagen ni en `cermed.conf`, pero las bibliotecas y módulos están instalados. Hace falta cerrar la revisión de otros consumidores. |

Las filas TIFF/curl/libxml2 describen la imagen anterior: esos componentes ya
no están presentes en la imagen reducida. Las conclusiones restantes no se
convirtieron en exclusiones por supuesta ausencia de rutas de explotación.

### MariaDB: versión instalada ya corregida

La [tabla oficial de correcciones de MariaDB 10.11](https://github.com/mariadb-corporation/mariadb-docs/blob/main/release-notes/community-server/10.11/what-is-mariadb-1011.md)
confirma que **10.11.19** corrige los ocho avisos que Grype todavía asocia al
paquete fuente: CVE-2026-107815, 107818, 107821, 107823, 85746, 86047, 92262
y 97380. La imagen contiene `1:10.11.19-0+deb12u1`.

El [aviso CVE-2026-86047](https://github.com/MariaDB/server/security/advisories/GHSA-wxr3-wm3p-7w6p)
sí incluye `mariadb-dump`; no basta con decir que falta el servidor. Se comprobó
que el cliente de dumps instalado también es 10.11.19, versión corregida.

Se agregaron ocho reglas, limitadas a cada CVE, Debian 12, tipo deb, versión
exacta y cuatro nombres de paquetes cliente enumerados. Excluyen 32 coincidencias
(24 High y 8 Critical), conservadas en `ignoredMatches`. La comparación del JSON
verificó que todos los demás matches permanecen iguales: **92 High / 5 Critical**
pendientes en web. No se excluyen versiones futuras ni paquetes de servidor.
Informe: `/tmp/cermed-web-reviewed-scan/image-1.json`.

## Coincidencias Oracle contra paquetes FIPS

Los avisos [ELSA-2026-500448](https://linux.oracle.com/errata/ELSA-2026-500448.html),
[ELSA-2026-50075](https://linux.oracle.com/errata/ELSA-2026-50075.html) y
[ELSA-2026-50346](https://linux.oracle.com/errata/ELSA-2026-50346.html) ofrecen
paquetes del canal de validación FIPS con epoch 10. La imagen tiene paquetes
no FIPS: OpenSSL `1:3.5.8-2.0.1.el9_8` y GnuTLS `3.8.10-9.el9_8`.

Se confirmó el cruce incorrecto de variantes con los errata no FIPS:

- [ELSA-2026-1473](https://linux.oracle.com/errata/ELSA-2026-1473.html) corrige los
  mismos CVE de 50075 desde OpenSSL `1:3.5.1-7.0.1.el9_7`, anterior al instalado.
- [ELSA-2026-77396](https://linux.oracle.com/errata/ELSA-2026-77396.html) publica
  exactamente `1:3.5.8-2.0.1.el9_8` para CVE-2026-84782, el aviso de 500448.
  El changelog del RPM instalado también registra esa corrección.
- [ELSA-2026-20612](https://linux.oracle.com/errata/ELSA-2026-20612.html) contiene
  las correcciones de 50346 desde GnuTLS `3.8.10-4.el9_8`; el RPM instalado
  `3.8.10-9.el9_8` conserva esa entrada en su changelog.

`config/grype.yaml` excluye únicamente las cinco combinaciones de aviso,
namespace Oracle Linux 9, tipo RPM, nombre y versión exactos. Las reglas no
incluyen aliases ni versiones futuras; un cambio de paquete exige reevaluarlas.
El JSON conserva las cinco coincidencias en `ignoredMatches`, con su motivo.
Se siguió el [formato de filtros de Grype](https://oss.anchore.com/docs/guides/vulnerability/filter-results/).

Validación: MySQL sale con código 0 y sin High/Critical pendientes; los cinco
matches excluidos son exactamente la diferencia respecto del informe sin reglas.
Los demás matches de MySQL y todos los de web/Nginx permanecen idénticos. El
script sigue fallando para web y Nginx. No se instala FIPS ni se acepta una
vulnerabilidad sin parche para lograr este resultado.

## Lo que todavía falta

- Cerrar tres avisos Critical distintos que todavía no tienen exclusión:

  | Aviso | Condición relevante y pendiente |
  | --- | --- |
  | CVE-2026-5450, web/glibc, 4 matches | Requiere `scanf` con `%mc` y ancho mayor a 1024. Debian Bookworm no ofrece parche; falta revisar consumidores nativos. No se considera resuelto por ausencia de llamadas en el código Python. |
  | CVE-2025-7458, web/SQLite, 1 match | Requiere SQL arbitrario contra SQLite. Producción usa MySQL y solo `test_settings.py` configura SQLite en el repo; la biblioteca permanece instalada. No se excluyó automáticamente. |
  | CVE-2026-19445, Nginx/Python, 4 matches | Requiere un servidor TLS Python con cambio de contexto SNI. La configuración usa TLS Nginx y Certbot webroot; revisar también configuración/hooks del servidor antes de cerrar su aplicabilidad. |

- Completar los demás avisos High/Critical, distinguiendo componente, versión y
  ruta de ejecución. Los conteos completos están en `UPGRADE-VALIDATION.md`.
- Mantener los avisos sin parche o sin conclusión como pendientes; no usar una
  exclusión global por paquete o por severidad.

Se consultó también la [base oficial de Debian](https://security-tracker.debian.org/tracker/data/json)
para los avisos pendientes. Varias entradas están aplazadas o marcadas como
menores por Debian, aunque Grype use High/Critical. Eso no equivale a un parche
ni autoriza una excepción global. Certbot sigue en la versión de Debian 4.0.0;
sus dependencias `python3-urllib3` y `python3-cryptography` tienen avisos abiertos.
Una siguiente mejora posible es actualizar Certbot en un entorno virtual con
lock propio, manteniendo webroot y verificando los hooks reales; todavía no se
implementó ni validó ese cambio.

Fuentes del ensayo: `/tmp/cermed-mysql-runtime-build.log` y
`/tmp/cermed-mysql-runtime-scan/image-1.json`. No hay datos de pacientes en estos
informes de imágenes. Escaneos con reglas: `/tmp/cermed-mysql-scoped-scan/` y
`/tmp/cermed-scoped-other-scans/`. La validación funcional se registra por separado.
