# Actualización Expat — 2026-11-10

El CI detectó CVE-2026-117610 y CVE-2026-118370 en Expat 2.9.0
integrado en CPython. [Expat 2.10.0](https://github.com/libexpat/libexpat/blob/R_2_10_0/expat/Changes)
corrige ambos avisos y los dos anteriormente aceptados, CVE-2026-113351 y
CVE-2026-115506. Las publicaciones oficiales Python 3.12.16, 3.13.18 y 3.14.10
todavía incluyen Expat 2.9.0.

Los Dockerfile de desarrollo, producción y Nginx compilan `pyexpat` desde la
misma versión de CPython que ejecutan, enlazando estáticamente Expat 2.10.0.
Ambos archivos fuente quedan fijados por SHA-256. Solo se copia la extensión
resultante al runtime; compiladores y fuentes quedan en la etapa de build.
El build verifica la versión cargada y parsing con pyexpat y ElementTree.
Esto permite conservar Python 3.12 para Django y Python 3.13 para Certbot.

Se retiran las dos excepciones anteriores de Expat y se actualizan los hashes
de los Dockerfile y del nuevo script en la política. Las otras aceptaciones
previas conservan su alcance y versiones exactas; no se agregan excepciones.
El escaneo complementario sigue inventariando la versión real de pyexpat.

Validación local: 14 pruebas de la política, sintaxis del script y compilación
nativa de pyexpat desde CPython 3.12.16 con Expat 2.10.0. La extensión compilada
reporta `expat_2.10.0` y procesa XML; `ldd` confirma que no depende de la
biblioteca compartida Expat del sistema. El build Docker,
la prueba funcional de Nginx y el escaneo completo quedan pendientes de CI:
el usuario local no tiene acceso al daemon y sudo requiere contraseña.
Las secciones siguientes conservan la evidencia histórica de revisiones previas.


# Revisión de avisos de imágenes — 24/10/2026

## Decisión de despliegue autorizada — 31/10/2026

Tras la revisión de los 14 CVE High restantes, el usuario pidió salir del bloqueo
y desplegar la versión. Se registra **aceptación de riesgo residual** para esta
configuración, no una declaración de que los componentes estén corregidos.
La evidencia y las limitaciones de cada componente se mantienen más abajo.

`config/reviewed-image-risk.json` limita la decisión a los CVE, roles de imagen,
paquetes, versiones, namespaces y estados de corrección revisados. Los hashes
de Dockerfiles, locks, Compose, configuración y controles vinculan la aceptación
a este runtime. Web y Nginx declaran `SYS_ADMIN` eliminado y
`no-new-privileges`; los ensayos se ejecutan con esas restricciones.

CI usa `scan-upgrade-images.sh --accept-reviewed-risk` con los tres roles en orden
web/nginx/mysql. Grype sigue generando todos los matches; el evaluador posterior
rechaza Critical/Unknown, High nuevos, cambios de versión/namespace/tipo/rol,
correcciones disponibles, explotación conocida indicada por Grype, evidencia
inválida, otra arquitectura y una base de vulnerabilidades de más de cinco días.
Los SBOM de Expat quedan vinculados al ID de imagen y se evalúan también.
El modo sin esa opción conserva el bloqueo estricto por High.

No existe una fecha arbitraria de desbloqueo/caducidad: un cambio en los archivos
vinculados o en los hallazgos exige revisar la decisión. El escaneo se repite en
cada CI; la aceptación y los informes permanecen visibles. Cambiar condiciones
de producción (privilegios, montajes, exposición de servicios o procesamiento de
entradas) exige reevaluación aunque no cambien los CVE.

Validación local: 14 pruebas del gate, 60 tests Django, backup/restauración con TLS,
Nginx/Certbot con las restricciones y escaneo completo con **cero bloqueos fuera
de los riesgos aceptados**. MySQL no requiere aceptación High. Evidencia:
`/tmp/cermed-release-policy-scans/`, `/tmp/cermed-release-policy-{app,proxy}.log`.
La puerta `CERMED_MYSQL84_READY` permanece cerrada hasta completar y validar la
migración productiva. Esta decisión no autoriza reutilizar el volumen 5.7 en 8.4.

## Aviso nuevo de glibc aceptado de forma acotada — 31/10/2026

El run `41209359838` reconstruyó las mismas imágenes tras un cambio solo de
documentación, pero la base de Grype pasó de `2026-10-30T06:23:28Z` a
`2026-10-31T06:18:17Z`. La base nueva incorporó
[CVE-2026-84243](https://security-tracker.debian.org/tracker/CVE-2026-84243):
cuatro coincidencias de glibc en web y dos en Nginx. El gate falló como estaba
diseñado; no fue una regresión del runtime. Debian mantiene Trixie
`2.41-12+deb13u4` vulnerable y todavía no publica una versión corregida.

El fallo permite que la familia `gettext` recorra rutas mediante entradas
maliciosas de `LANGUAGE`. La explotación requiere además un locale de mensajes
distinto de C, poder colocar un catálogo `.mo` legible y cruzar un límite de
confianza con el entorno del proceso. No se encontraron catálogos `.mo` del
proyecto, una vía HTTP que modifique el entorno ni SSH/`AcceptEnv` dentro de los
contenedores. Esto reduce exposición, pero no corrige glibc ni convierte el
hallazgo en falso positivo.

Web fija al arrancar `LANG=es_AR.UTF-8`, `LANGUAGE=es_AR:es` y
`LC_ALL=es_AR.UTF-8`; ninguna entrada de `LANGUAGE` contiene `/` ni es `..`.
Nginx fija el locale C y `LANGUAGE=C`. El control de imagen comprueba tanto los
defaults incorporados como los exports de ambos entrypoints. La política separa
roles: web acepta solamente `libc-bin`, `libc-l10n`, `libc6` y `locales`; Nginx
solamente `libc-bin` y `libc6`, siempre en la versión exacta observada y con
estado `not-fixed`.

El usuario autorizó esta aceptación residual adicional después de la revisión.
El inventario resultante conserva **53 High de catálogo + 2 de Expat** en web y
**41 + 2** en Nginx, correspondientes a 14 y 12 CVE High distintos; MySQL sigue
en cero High. Una versión corregida, explotación conocida, otro paquete, versión,
rol, namespace o estado vuelve a cerrar el gate automáticamente. No se parchea
glibc a mano ni se cambia de distribución por este aviso aislado.

Validación final: 14 pruebas del gate, construcción de web/Nginx/MySQL, control
de componentes y locales, `manage.py check`, smoke completo de Nginx/Certbot y
escaneo fresco de las tres imágenes terminaron correctamente. El escaneo preserva
todos los hallazgos y devuelve cero bloqueos; evidencia local en
`/tmp/cermed-cve-84243-final-scans/`.

## Revisión de todos los High y actualización adicional — 31/10/2026

Se cruzaron los **17 CVE High distintos** de las candidatas anteriores con
los avisos de Debian/upstream, los componentes instalados y sus usos en CERMED.
También se inventariaron las demás severidades y sus actualizaciones disponibles.
Los hallazgos sin resolución se conservan: revisión no equivale a aceptación.

Resultado previo al aviso nuevo (coincidencias por paquete; **0 Critical** en las tres):

| Imagen | High del catálogo | High de Expat integrado | CVE High distintos | Medium / Low / Negligible |
| --- | ---: | ---: | ---: | --- |
| Web | 49 | 2 | 13 | 152 / 24 / 72 |
| Nginx | 39 | 2 | 11 | 54 / 12 / 56 |
| MySQL | 0 | 0 | 0 | 13 / 0 / 0 |

Los dos avisos agregados a web son cobertura nueva, no una regresión de versión.
En Nginx, 16 coincidencias desaparecen por los cuatro CVE de Python corregidos;
las dos de Expat cambian de catálogo a SBOM. Los avisos de pip desaparecen.
MySQL baja de 16 a 13 Medium al corregir xz y gosu. Los avisos restantes no se
excluyen. **El gate High sigue fallando y el despliegue continúa bloqueado.**

Pasaron: construcción de las cuatro imágenes (web prod/dev, Nginx, MySQL),
`check-mysql-client.sh` con **60 tests**, backup/restauración y negativos TLS,
`check-nginx-image.sh` con proxy/archivos/ACME/cron y hostname TLS, controles
de componentes ausentes, y `pip-audit` de ambos locks de producción/Certbot.
Permanece el warning de URL preexistente; no se ejecutó una emisión ACME real.
El ensayo Excel fue rojo antes y verde después. El escaneo SBOM detecta los
dos CVE reales de Expat, conserva JSON y devuelve error; MySQL sin Python se
escanea correctamente y pasa el umbral High.

Evidencia: `/tmp/cermed-full-review-scans/` para web/proxy y
`/tmp/cermed-full-review-mysql-scans/` para MySQL final;
`/tmp/cermed-full-review-app-final.log`, `/tmp/cermed-full-review-proxy-check.log`,
`/tmp/cermed-full-review-pip-audit.log` y `/tmp/cermed-excel-entities-red.log`.
No hubo push ni cambios en el droplet. La reversión de este paso restaura los
Dockerfiles, locks, test Excel, comprobación del proxy y escaneo complementario
como una unidad, sin revertir las mejoras TLS y de herramientas del paso anterior.

### Correcciones aplicadas

- Certbot usa ahora **Python 3.13.18 oficial**, fijado por digest, sobre el mismo
  Debian Trixie de Nginx. Se copian el intérprete y su biblioteca estándar y se
  instalan sus dependencias nativas mediante APT; no se mezclan distribuciones.
  Se corrigen los cuatro avisos High del Python Debian anterior:
  [HTMLParser](https://security-tracker.debian.org/tracker/CVE-2026-15308),
  [hostname TLS](https://security-tracker.debian.org/tracker/CVE-2026-19553),
  [entropía XML](https://security-tracker.debian.org/tracker/CVE-2026-7210) y
  [filtros tar](https://security-tracker.debian.org/tracker/CVE-2026-82049).
  Se retira la antigua excepción de SNI para Python Debian 3.13.5.
- `pip` queda en **26.2.2** tanto globalmente como en los venv. La actualización
  previa solo alcanzaba al venv web; se verificó la desaparición de sus hallazgos
  en el escaneo completo, sin filtros nuevos.
- Producción incorpora **defusedxml 0.7.1**, con hashes, para las importaciones
  Excel mediante pandas/openpyxl. [Openpyxl recomienda esta protección](https://openpyxl.readthedocs.io/en/stable/#security).
  Un XLSX sintético con una sola entidad se aceptaba antes; ahora el lector real
  lo rechaza con `EntitiesForbidden`. El test de Excel normal sigue pasando.
  Esto mitiga expansión de entidades; no parchea Expat ni evita todos los posibles
  consumos excesivos de recursos al importar archivos.
- MySQL mantiene **8.4.13**, actualiza todos los RPM disponibles de Oracle
  (incluidos xz, curl/libcurl y krb5-libs) y usa **gosu 1.20** del mantenedor,
  fijado por digest. [Oracle corrige xz](https://linux.oracle.com/errata/ELSA-2026-89749.html)
  y [gosu incorpora moby/sys/user 0.4.1](https://github.com/tianon/gosu/releases/tag/1.20).
  Se conserva el entrypoint original y se verifica el cambio al usuario MySQL.

### Expat estaba fuera del inventario web

Tanto Python web 3.12.16 como el Python 3.13.18 de Certbot cargan **Expat 2.9.0**.
Quitar el paquete Debian de Python elimina `libexpat1` del catálogo, pero deja
la copia integrada vulnerable. Por eso no se cuentan esos dos avisos como resueltos.
`python-expat-sbom.py` obtiene la versión cargada y emite CycloneDX con el CPE del
[SBOM oficial de Python](https://www.python.org/ftp/python/3.13.18/Python-3.13.18.tar.xz.spdx.json).
`scan-upgrade-images.sh` lo escanea con la misma base Grype y bloqueo High.
CI conserva tanto los SBOM como los informes; cualquier fallo de inventario o
escaneo falla el paso. MySQL no tiene intérprete Python y conserva su escaneo de imagen.
No se agregó una lista manual de vulnerabilidades ni una excepción para Expat.

### Hallazgos High pendientes, con alcance y acción

| Componente / CVE | Evidencia y alcance | Resolución pendiente |
| --- | --- | --- |
| glibc: [19499](https://security-tracker.debian.org/tracker/CVE-2026-19499), [5435](https://security-tracker.debian.org/tracker/CVE-2026-5435) | `strfmon` y funciones antiguas de impresión DNS. No hay llamadas directas en el proyecto; `locale.currency()` de Python formatea en Python, no mediante `strfmon`. Esto no prueba ausencia de uso en todas las dependencias nativas. | Debian Trixie 2.41-12+deb13u4 sigue afectado. Esperar paquete corregido o ensayar otra base completa. No reemplazar libc aisladamente. |
| util-linux: [76642](https://security-tracker.debian.org/tracker/CVE-2026-76642), [78409](https://security-tracker.debian.org/tracker/CVE-2026-78409), [78410](https://security-tracker.debian.org/tracker/CVE-2026-78410) | Fallos de montajes privilegiados/fstab. El droplet reportó kernel 5.15, sin privilegios extra y sin entradas fstab; 78409 exige Linux ≥6.15. Son condiciones que reducen exposición, no bibliotecas corregidas. | `libmount` permanece instalado; 2.41.5 de Trixie no tiene el arreglo. No ampliar la excepción de `nsenter` a estos avisos. |
| GCC/libstdc++: [102010](https://security-tracker.debian.org/tracker/CVE-2026-102010), [95619](https://security-tracker.debian.org/tracker/CVE-2026-95619) | PBDS `erase_if` y asignación alineada. La ausencia de compilador en runtime no demuestra que las extensiones compiladas no incluyan código afectado. | GCC 14.2 de Trixie sin arreglo disponible. El caso de plantillas puede requerir reconstruir consumidores además de actualizar bibliotecas. |
| ACL: [54369](https://security-tracker.debian.org/tracker/CVE-2026-54369) | Carreras de rutas/symlinks al manejar ACL con privilegios. La biblioteca sigue presente aunque se hayan quitado herramientas CLI. | Trixie 2.3.2; upstream 2.4.0 añade ABI, con incompatibilidades documentadas. No aplicar un parche parcial ni extender la excepción de CLI. |
| Perl: [82560](https://security-tracker.debian.org/tracker/CVE-2026-82560), [9538](https://security-tracker.debian.org/tracker/CVE-2026-9538) | `Pod::Text` y `Archive::Tar` presentes solo en web. No hay llamadas Perl del proyecto; MariaDB cliente depende de Perl y una purga elimina `mysqldump`. | No hay actualización de Trixie. Los módulos tienen arreglos upstream, pero integrar CPAN o recortar módulos exige validar herramientas cliente; el tracker señala regresiones pendientes en Archive::Tar. No se ocultaron. |
| zlib: [85091](https://security-tracker.debian.org/tracker/CVE-2026-85091) | La descripción indica versiones posteriores a 1.3.1, pero Debian marca la instalada como afectada y mantiene la [discusión de alcance](https://github.com/madler/zlib/issues/1310). | Se mantiene el hallazgo hasta confirmar el alcance con el proveedor o actualizar a un paquete corregido; no se descarta solo por comparar números de versión. |
| Expat: [113351](https://security-tracker.debian.org/tracker/CVE-2026-113351), [115506](https://security-tracker.debian.org/tracker/CVE-2026-115506) | Agotamiento de recursos por reset de parsers y expansión de entidades. También presentes en las copias integradas de Python. Se protegió la vía Excel conocida, sin declarar toda la biblioteca segura. | Seguimiento upstream abierto; 2.9.0 y los paquetes Debian disponibles siguen afectados. Actualizar Python/Expat cuando integren ambos arreglos y repetir el escaneo complementario. |

Todos los CVE de la tabla son de 2026. La consulta de APT estable, security y
backports confirmó que no hay versiones superiores para estas bibliotecas;
no se añadió backports a los Dockerfiles. La tabla cubre los **13 High distintos
que siguen presentes** entre web y proxy, incluidos los dos de Expat descubiertos
en web. No identifica una explotación remota demostrada de los otros componentes,
pero tampoco certifica que sus rutas sean inalcanzables.

### Otras severidades y límites

Se mantienen los Medium/Low/Negligible completos en los JSON. Incluyen avisos de
glibc, util-linux, Perl, ncurses, tar, PAM, systemd, SQLite, attr/bzip2, MariaDB
cliente y funciones de Python. La aplicación no usa IMAP/POP ni `Morsel.js_output`
directamente; usa MySQL en producción y SQLite solo en configuración de tests.
No se crearon exclusiones a partir de esas búsquedas. Los avisos con corrección
en otra rama de Python no justifican saltar de versión de la aplicación sin
una validación de compatibilidad separada.

En MySQL, los avisos Medium restantes comparan paquetes no FIPS con versiones
FIPS de epoch 10: OpenSSL (ELSA-2024-12675, 2025-28011, 2026-50379, 2026-50345),
GnuTLS (ELSA-2024-12336, 2024-12364, 2025-20606, 2026-50149) y libgcrypt
(ELSA-2026-500145). Se conserva la evidencia en los informes; no se agregaron
excepciones Medium por analogía con las High ya justificadas.

Esta revisión cubre imágenes, paquetes y las vías de uso señaladas; no sustituye
una auditoría completa de autorización, lógica de negocio o un análisis forense
del droplet. La exposición productiva debe verificarse otra vez al desplegar:
8000 debe quedar en loopback, MySQL exige TLS y el acceso a 3308 sigue sujeto
al firewall/uso autorizado existente. No se modificó producción.

## Retiro de herramientas sin uso — 31/10/2026, validado localmente

Web y Nginx ya no incluyen `nsenter` ni `infocmp`; no hay llamadas a estas
herramientas en la aplicación ni en los scripts operativos del repositorio.
[CVE-2026-78408](https://security-tracker.debian.org/tracker/CVE-2026-78408)
afecta a `nsenter --join-cgroup` y
[CVE-2025-69720](https://security-tracker.debian.org/tracker/CVE-2025-69720)
a `progs/infocmp.c`. Se eliminan los ejecutables existentes y
`config/dpkg-runtime-excludes` impide reinstalarlos al actualizar sus paquetes.
Una reinstalación real en un contenedor desechable confirmó ambas ausencias;
`flock` y `tput` siguen disponibles.

Grype asocia estos avisos también a otros paquetes binarios del mismo código
fuente. Las reglas se limitan a esos dos CVE, Debian 13 y nombres/versiones
exactos; las coincidencias permanecen en `ignoredMatches`. CI verifica la
ausencia de ejecutables antes del escaneo y falla con la imagen anterior.
Las bibliotecas retenidas no se declaran parcheadas: siguen visibles los otros
tres avisos de util-linux (76642, 78409 y 78410, todos CVE-2026), sin versiones
corregidas disponibles en Trixie estable o backports durante esta revisión.

Resultado: web **49 High / 0 Critical** (antes 63), Nginx **57 High / 0 Critical**
(antes 70). Son coincidencias por paquete: corresponden a 11 y 15 CVE High
distintos, respectivamente. La comparación de JSON confirma que solo se retiraron
14 y 13 coincidencias de los dos ejecutables; no hubo otros cambios de hallazgos.
**CI sigue bloqueando por High.** No se habilitó ninguna aceptación temporal.

Validación: `check-mysql-client.sh` pasó los 59 tests, backup/restauración y
rechazo de host/CA incorrectos y TCP sin TLS. `check-nginx-image.sh` pasó TLS,
proxy, estáticos/media, ACME, Certbot y cron, incluido fallo sin recarga.
Se mantiene el warning de URL preexistente. Informes en
`/tmp/cermed-reduced-tools-scans/image-{1,2}.json`; logs de pruebas en
`/tmp/cermed-reduced-tools-{mysql,nginx}-check.log`.
El cambio se revierte como una unidad: exclusiones dpkg, eliminación en los tres
Dockerfiles, reglas de esos dos CVE y su control de ausencia. No se hizo push
ni despliegue productivo.

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
