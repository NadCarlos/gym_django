# Investigación de bloqueos de escritura

## Resumen

El código no usa `ATOMIC_REQUESTS` ni transacciones manuales globales. Antes de
estos cambios, los únicos `transaction.atomic()` web estaban en altas clínicas
y contenían solo escrituras relacionadas; el render y la generación de PDF
quedan fuera. No hay señales `pre_save`, `post_save`, `post_delete` o
`m2m_changed`, ni llamadas HTTP externas en los flujos revisados.

El riesgo principal es la combinación de lock waits largos de InnoDB con ocho
threads de Gunicorn, escrituras repetibles desde formularios y bajas que antes
hacían varios `save()` por registro. Con el timeout por defecto de InnoDB,
varias requests bloqueadas pueden ocupar todos los threads antes del timeout de
Nginx y producir la mezcla observada de 200, 499 y 504.

## Cambios aplicados

- `WriteDatabaseInstrumentationMiddleware` registra inicio, resolución de
  vista, fin, usuario, request ID, status, duración, cantidad de queries y tiempo
  acumulado de DB para POST/PUT/PATCH/DELETE.
- Los bloques atómicos críticos registran por separado su duración exacta,
  operación y resultado `commit`/`rollback`, correlacionados con la misma
  request.
- Las queries que superan `DB_SLOW_QUERY_MS` registran SQL sin parámetros y
  truncado a 2000 caracteres para evitar PII excesiva.
- Los errores MySQL 1205 y 1213 se registran y responden 503 con
  `Retry-After: 1`.
- Cada conexión fija `innodb_lock_wait_timeout=5`; esto evita que un lock
  bloqueado retenga un thread durante decenas de segundos.
- Las bajas críticas de turnos, agendas y pacientes usan POST con CSRF.
- La creación de turnos usa un `request_token` UUID con constraint única. Un
  reenvío devuelve el turno ya creado.
- Cada baja de agenda hace un solo UPDATE; las bajas masivas de agenda por
  paciente también usan un solo UPDATE.
- La asignación paciente-área se serializa con un lock corto y determinista
  sobre la fila de `Area`.
- Se agregaron índices compuestos para los filtros por profesional/paciente,
  activo, fecha/día y hora.
- Se eliminó el N+1 de turno cercano en el listado de Fisiatría.

## Hallazgos que requieren datos de producción

### Transacciones y blockers actuales

Ejecutar mientras el incidente está ocurriendo:

```sql
SHOW FULL PROCESSLIST;
SHOW ENGINE INNODB STATUS\G

SELECT
    waiting.trx_mysql_thread_id AS waiting_thread,
    waiting.trx_started AS waiting_started,
    waiting.trx_query AS waiting_query,
    blocking.trx_mysql_thread_id AS blocking_thread,
    blocking.trx_started AS blocking_started,
    blocking.trx_query AS blocking_query,
    locks.lock_table,
    locks.lock_index,
    locks.lock_type,
    locks.lock_mode
FROM information_schema.innodb_lock_waits waits
JOIN information_schema.innodb_trx waiting
  ON waiting.trx_id = waits.requesting_trx_id
JOIN information_schema.innodb_trx blocking
  ON blocking.trx_id = waits.blocking_trx_id
JOIN information_schema.innodb_locks locks
  ON locks.lock_id = waits.requested_lock_id
ORDER BY waiting.trx_started;
```

También conviene capturar:

```sql
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
SHOW VARIABLES LIKE 'tx_isolation';
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Threads_running';
```

Correlacionar el timestamp y la URL con los logs `[DB-WRITE]`. El
`request_id` permite unir `start`, `transaction`, `slow_sql`, `lock_error` y
`finish`.

### Duplicados previos a nuevas constraints

El código asume un paciente por DNI y una relación por paciente/área, pero la
base todavía no lo garantiza. Antes de agregar constraints, ejecutar:

```sql
SELECT numero_dni, COUNT(*) AS total, GROUP_CONCAT(id ORDER BY id) AS ids
FROM administracion_paciente
GROUP BY numero_dni
HAVING COUNT(*) > 1;

SELECT id_area_id, id_paciente_id, COUNT(*) AS total,
       GROUP_CONCAT(id ORDER BY id) AS ids
FROM administracion_pacientearea
WHERE id_paciente_id IS NOT NULL
GROUP BY id_area_id, id_paciente_id
HAVING COUNT(*) > 1;

SELECT request_token, COUNT(*) AS total
FROM rehabilitacion_turno
WHERE request_token IS NOT NULL
GROUP BY request_token
HAVING COUNT(*) > 1;
```

Después de revisar y consolidar los datos, las constraints recomendadas son:

1. `UNIQUE administracion_paciente(numero_dni)`.
2. `UNIQUE administracion_pacientearea(id_area_id, id_paciente_id)`.
3. Para disponibilidad de turnos, una clave única materializada y nullable que
   represente `profesional + fecha + hora` solo cuando el turno ocupa el slot.

MySQL 5.7 no soporta índices únicos parciales. No se agregó una unicidad directa
`(profesional, fecha, hora, activo)` porque impediría conservar más de un
registro histórico inactivo y no define si un turno anulado libera el slot.
Esa regla de negocio debe fijarse antes de migrar datos.

Las agendas usan intervalos, por lo que una constraint única simple no evita
solapamientos. Si la disponibilidad debe ser estricta, conviene modelar slots
discretos en una tabla con clave única y reservarlos dentro de un
`transaction.atomic()` corto.

## Índices agregados

- `rehabilitacion_turno(profesional_id, activo, fecha, hora)`
- `rehabilitacion_turno(paciente_id, activo, fecha, hora)`
- `rehabilitacion_agendarehab(id_paciente_area_id, activo, id_dia_id, hora_inicio)`
- `rehabilitacion_agendarehab(id_profesional_area_id, activo, id_dia_id, hora_inicio)`
- `administracion_agenda(id_prestacion_paciente_id, activo, id_dia_id, hora_inicio)`
- `administracion_agenda(id_profesional_tratamiento_id, activo, id_dia_id, hora_inicio)`
- `administracion_paciente(numero_dni)`
- `administracion_pacientearea(id_area_id, activo, id_paciente_id)`

Validar planes con `EXPLAIN` usando los parámetros de una request lenta real.

## Preflight de migraciones

No aplicar estas migraciones a ciegas. Primero confirmar que Django reconoce el
historial ya desplegado y que no pretende recrear el esquema de una base
poblada:

```bash
python manage.py showmigrations administracion rehabilitacion
python manage.py migrate --plan
```

Los `AddIndex` pueden esperar un metadata lock aunque InnoDB construya el índice
online. Ejecutarlos en una ventana de baja actividad, con backup verificado, de
a uno por vez si las tablas son grandes y observando `SHOW PROCESSLIST`. Revisar
el SQL exacto con `sqlmigrate` antes del deploy.

Si `migrate --plan` enumera migraciones iniciales sobre tablas que ya existen,
detener el despliegue: primero hay que reconciliar el historial con el esquema
actual. Usar `--fake` solamente después de comparar cada migración con la base;
resolverlo por intuición puede dejar el estado de Django inconsistente.

## Activación y retiro de instrumentación

Variables:

```dotenv
DB_LOCK_WAIT_TIMEOUT=5
DB_SLOW_QUERY_MS=250
WRITE_DB_INSTRUMENTATION_ENABLED=True
REQUEST_INSTRUMENTATION_ENABLED=True
SLOW_REQUEST_LOG_MS=2000
SLOW_REQUEST_STACK_MS=10000
SLOW_REQUEST_WATCHDOG_ENABLED=True
```

Mantener la instrumentación durante el período de diagnóstico. El watchdog es temporal: registra una vez el stack Python de cada request activa que alcanza `SLOW_REQUEST_STACK_MS`; buscar `[SLOW-REQUEST] stack` y correlacionar su `request_id`, `pid` y `thread_id` con `[SLOW-REQUEST] finish` y `[DB-QUERY] slow_sql`.

Después de capturar evidencia suficiente, desactivarlo con `SLOW_REQUEST_WATCHDOG_ENABLED=False`; mantener los logs resumidos de requests lentas. Mantener el lock wait timeout corto
si la tasa de 503 es aceptable; un 503 rápido y reintentable protege los threads
mejor que un 504 tardío.

No aumentar los timeouts de Nginx o Gunicorn como solución principal.
