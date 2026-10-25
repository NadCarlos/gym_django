# Prueba funcional de la actualización

Abrí **http://127.0.0.1:18000/usuarios/login/** en esta computadora.
La copia local ya está iniciada, con el backup real del 24/10/2026 y la imagen
MySQL corregida. Comprobé HTTP 200 en login, admin y archivos estáticos.

Los cambios que hagas aquí quedan en la copia local. Producción no está conectada.
Web y MySQL permanecen en una red interna; solo el proxy publica
`127.0.0.1:18000`. Cron y Sentry están desactivados. El servidor de desarrollo
sirve estáticos para esta prueba; esto no valida HTTPS o Nginx de producción.

1. Entrá con tu usuario habitual. No compartas la contraseña. Comprobá que
   llegás al área correspondiente y que ves las opciones de tu rol.
2. Abrí listados y fichas de pacientes/profesionales. Revisá fechas, importes,
   caracteres acentuados y filtros.
3. Abrí una agenda, seleccioná profesional/tratamiento y creá/modificá un turno
   de prueba en esta copia. Verificá la redirección y el resultado visible.
4. Revisá cuotas/pagos o finanzas según tu rol. Registrá una operación ficticia
   en esta copia y comprobá los importes y listados afectados.
5. Descargá un PDF y un XLSX habituales y abrilos. Comprobá formato, fechas e
   importes. No adjuntes archivos con datos de pacientes al chat.
6. Cerrá sesión y volvé a entrar. Si tenés otra cuenta con diferente rol,
   repetí la comprobación de permisos con ella.

La base está copiada, pero **los medios subidos de producción no**: un adjunto
histórico puede faltar. Eso no demuestra una regresión. Los logos/estáticos del
repositorio sí están disponibles. Los tests automáticos pasaron; esta revisión
busca diferencias funcionales que esos tests no cubren.

Compartí qué pasos pasaron y cualquier pantalla/error que falle, sin datos de
pacientes. No hace falta ejecutar más comandos en el droplet en este paso.

## Detener o volver a abrir la copia

Desde la raíz del repositorio local, para detener los tres servicios conservando
los volúmenes:

```bash
docker compose --project-name cermed-upgrade-mysql-patched --env-file /dev/null \
  -f docker-compose-upgrade.yaml -f docker-compose-upgrade-preview.yaml stop
```

Para volver a abrirla:

```bash
docker compose --project-name cermed-upgrade-mysql-patched --env-file /dev/null \
  -f docker-compose-upgrade.yaml -f docker-compose-upgrade-preview.yaml up -d web preview
```

No usar `down --volumes` si querés conservar los cambios de esta prueba.
