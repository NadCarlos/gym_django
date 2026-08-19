# Resumen técnico — Errores 500 en el backoffice y fix aplicado

## Problema principal

El sistema presentaba **errores 500 intermitentes al guardar o editar registros**, sobre todo en la **agenda de rehabilitación** (editar un turno de un paciente). El comportamiento era: el operador cargaba el formulario, el sistema devolvía error, y al reintentar la operación "funcionaba". Esto apuntaba a que **no era un problema de base de datos ni de infraestructura**, sino de **lógica de la aplicación**.

## Causa raíz

Al auditar el código completo se encontraron **dos patrones repetidos en toda la base de código** (24 archivos de vistas):

**1. Formularios sin respuesta ante datos inválidos**
Cuando un formulario llegaba con datos incompletos, el sistema no tenía definido qué hacer y **fallaba con un error 500 genérico** en vez de volver a mostrar el formulario con el aviso correspondiente.

El caso más típico (y el que originó todo): los desplegables encadenados de profesional/tratamiento. Estos selectores arrancan **deshabilitados** y solo se habilitan después de una consulta automática al servidor. Si el operador enviaba el formulario **antes** de que esa consulta terminara, el campo llegaba vacío → el servidor recibía un dato faltante → 500.

**2. Operaciones que usaban registros sin verificar que existieran**
Varias acciones (borrar, reactivar, reasignar un paciente/profesional) asumían que el registro existía y lo usaban directamente. Si el registro no existía, el sistema reventaba con 500.

## Fix aplicado

- **En todos los formularios (38 puntos):** si los datos no son válidos, ahora el sistema **vuelve a mostrar el mismo formulario con lo que el operador ya cargó** y un mensaje indicando qué corregir. **Nunca más devuelve un 500 por esto.**
- **En las operaciones sobre registros (9 puntos):** ahora se **verifica que el registro exista** antes de usarlo; si no, se redirige a una página de error amigable.
- La **agenda de rehabilitación** (el caso reportado) y la **agenda de gimnasio** —que tenían exactamente el mismo problema con los selectores encadenados— fueron las primeras en corregirse.
- Se agregaron **tests de regresión** para que este tipo de error no vuelva a aparecer.
- La agenda de rehabilitación y gimnasio muestran ahora un mensaje visible ("revise los campos") cuando el formulario no puede guardarse.

## Alcance e impacto

- **24 archivos de vistas** de los 6 módulos del sistema (administración, rehabilitación, finanzas, entrada, agenda, altas).
- **Sin cambios de base de datos**: no hay migraciones, ni cambios de modelo, ni de esquema.
- **Riesgo bajo**: el comportamiento normal de guardado no cambió; solo se agregó el camino de "formulario inválido" y las verificaciones de existencia.
- Validación: chequeos de Django correctos, tests de regresión pasando (13/13), y todos los formularios/templates afectados verificados.

## Recomendaciones

1. **Desplegar el fix a producción** y monitorear en Sentry que no reaparezcan 500 de este tipo.
2. **A futuro**: revisar los selectores encadenados para que no dependan de que el operador "espere" la carga automática (ya se agregó la marca de campo obligatorio, pero conviene blindar la experiencia de usuario).
3. Revisar unas vistas de borrado que todavía se ejecutan por GET (deberían ser solo por POST) — es una mejora de seguridad pendiente, no parte de este fix.