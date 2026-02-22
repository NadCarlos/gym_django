from django.urls import path

from rehabilitacion.views.inicio.index import(
    IndexView,
    DiagnosticosIndex,
)

from rehabilitacion.views.pacientes_rehab import(
    PacientesRehabList,
    PacienteRehabDetail,
    PacienteRehabCreate,
    PacienteRehabCreateFromExistent,
    PacienteRehabUpdate,
    PacienteRehabToCsv,
    PacienteAltasToCsv,
    PacienteRehabRedirectFromExistent,
    #PacientesRehabBulkAdd,
    PacienteRehabDelete,
)

from rehabilitacion.views.profesional_rehab import(
    ProfesionalRehabList,
    ProfesionalRehabDetail,
    ProfesionalRehabCreate,
    ProfesionalRehabCreateFromExistent,
    ProfesionalRehabUpdate,
)

from rehabilitacion.views.tratamiento_profesional_rehab import(
    TratamientoProfesionaRehablList,
    TratamientoProfesionalRehabCreate,
    TratamientoProfesionalRehabDelete,
)

from rehabilitacion.views.rehabilitacion import(
    RehabilitacionCreate,
    RehabilitacionUpdate,
)

from rehabilitacion.views.alta import(
    AltaCreate,
    DiagnosticoEtiologicoByTipoDiscapacidadView,
    AltaDetail,
    AltaTerminate,
    AltaFuncionalCreate,
    AltaFuncionalList,
    DiagnosticoFuncionalRemove,
)

from rehabilitacion.views.tipos_discapacidad import(
    TipoDiscapacidadList,
    TipoDiscapacidadCreate,
)

from rehabilitacion.views.diagnosticos_etiologicos import(
    DiagnosticosEtiologicosList,
    DiagnosticoEtiologicoCreate,
)

from rehabilitacion.views.diagnosticos_funcionales import(
    DiagnosticoFuncionalList,
    DiagnosticoFuncionalCreate,
)

from rehabilitacion.views.agenda import (
    AgendaProfesionalRehab,
    AgendaPacienteRehab,
    AgendaPacienteRehabCreate,
    AgendaPacienteRehabUpdate,
    AgendaRehabDelete,
)

from rehabilitacion.views.asistencia import (
    CheckInRehab,
    CheckInRehabErrorDni,
    CheckInRehabErrorAgendaActiva,
    CheckInRehabErrorAsistenciaRegistrada,
    CheckInRehabErrorDiaIncorrecto,
)

from rehabilitacion.views.informe import(
    InformesList,
    InformeCreate,
    InformeDetail,
)


inicio = [
    path(route='',view=IndexView.as_view(), name='inicio_rehab'),
    path(route='diagnosticos_index',view=DiagnosticosIndex.as_view(), name='diagnosticos_index'),
]

pacientes = [
    path(route='pacientes/list/<state>',view=PacientesRehabList.as_view(), name='pacientes_rehab_list'),
    path(route='pacientes/detail/<int:id>',view=PacienteRehabDetail.as_view(), name='paciente_rehab_detail'),
    path(route='pacientes/create',view=PacienteRehabCreate.as_view(), name='paciente_rehab_create'),
    path(route='pacientes/create_from_existent',view=PacienteRehabCreateFromExistent.as_view(), name='paciente_rehab_create_from_existent'),
    path(route='pacientes/update/<int:id>',view=PacienteRehabUpdate.as_view(), name='paciente_rehab_update'),
    path(route='pacientes/to_csv/<int:id>',view=PacienteRehabToCsv.as_view(), name='paciente_rehab_to_csv'),
    path(route='pacientes/altas_to_csv/<int:id>',view=PacienteAltasToCsv.as_view(), name='paciente_altas_rehab_to_csv'),
    path(route='pacientes/redirect_from_existent',view=PacienteRehabRedirectFromExistent.as_view(), name='paciente_rehab_redirect_from_existent'),
    #path(route='pacientes/bulk_add',view=PacientesRehabBulkAdd.as_view(), name='bulk_add'),
    path(route='pacientes/delete/<int:id>',view=PacienteRehabDelete.as_view(), name='paciente_rehab_delete'),
]

profesionales = [
    path(route='profesionales/list',view=ProfesionalRehabList.as_view(), name='profesional_rehab_list'),
    path(route='profesionales/detail/<int:id>',view=ProfesionalRehabDetail.as_view(), name='profesional_rehab_detail'),
    path(route='profesionales/create',view=ProfesionalRehabCreate.as_view(), name='profesional_rehab_create'),
    path(route='profesional/create_from_existent',view=ProfesionalRehabCreateFromExistent.as_view(), name='profesional_rehab_create_from_existent'),
    path(route='profesional/update/<int:id>',view=ProfesionalRehabUpdate.as_view(), name='profesional_rehab_update'),
]

tratamiento_profesional = [
    path(route='tratamiento_profesional/list/<int:id>',view=TratamientoProfesionaRehablList.as_view(), name='tratamiento_profesional_rehab_list'),
    path(route='tratamiento_profesional/create/<int:id>',view=TratamientoProfesionalRehabCreate.as_view(), name='tratamiento_profesional_rehab_create'),
    path(route='tratamiento_profesional/delete/<int:id>',view=TratamientoProfesionalRehabDelete.as_view(), name='tratamiento_profesional_rehab_delete'),
    #path(route='tratamientos/<int:profesional_id>/',view=TratamientosPorProfesionalView.as_view(), name='tratamientos_por_profesional'),
]

rehabilitacion = [
    path(route='rehabilitacion/create/<int:id>',view=RehabilitacionCreate.as_view(), name='rehab_create'),
    path(route='rehabilitacion/update/<int:id>',view=RehabilitacionUpdate.as_view(), name='rehab_update'),
]

alta = [
    path(route='alta/create/<int:id>',view=AltaCreate.as_view(), name='alta_create'),
    path(route="diagnosticos_etiologicos/<int:tipo_discapacidad_id>/", view=DiagnosticoEtiologicoByTipoDiscapacidadView.as_view(), name="get_diagnosticos_etiologicos_by_tipo_discapacidad"),
    path(route='alta/detail/<int:id>',view=AltaDetail.as_view(), name='alta_detail'),
    path(route='alta/terminate/<int:id>',view=AltaTerminate.as_view(), name='alta_terminate'),
    path(route='alta_funcional/create/<int:alta_id>',view=AltaFuncionalCreate.as_view(), name='alta_funcional_create'),
    path(route='alta_funcional/list/<int:alta_id>',view=AltaFuncionalList.as_view(), name='alta_funcional_list'),
    path(route='alta_funcional/remove/<int:alta_id>',view=DiagnosticoFuncionalRemove.as_view(), name='alta_funcional_remove'),
]

tipos_discapacidad = [
    path(route='diagnosticos/tipo_discapacidad/list',view=TipoDiscapacidadList.as_view(), name='tipo_discapacidad_list'),
    path(route='diagnosticos/tipo_discapacidad/create',view=TipoDiscapacidadCreate.as_view(), name='tipo_discapacidad_create'),
]

diagnosticos_etiologicos = [
    path(route='diagnosticos/diagnosticos_etiologicos/list',view=DiagnosticosEtiologicosList.as_view(), name='diagnosticos_etiologicos_list'),
    path(route='diagnosticos/diagnosticos_etiologicos/create',view=DiagnosticoEtiologicoCreate.as_view(), name='diagnosticos_etiologicos_create'),
]

diagnosticos_funcionales = [
    path(route='diagnosticos/diagnosticos_funcionales/list',view=DiagnosticoFuncionalList.as_view(), name='diagnosticos_funcionales_list'),
    path(route='diagnosticos/diagnosticos_funcionales/create',view=DiagnosticoFuncionalCreate.as_view(), name='diagnosticos_funcionales_create'),
]

agenda = [
    path(route='agenda_profesional_rehab/<int:id>',view=AgendaProfesionalRehab.as_view(), name='agenda_profesional_rehab'),
    path(route='agenda_paciente_rehab/<int:id>',view=AgendaPacienteRehab.as_view(), name='agenda_paciente_rehab'),
    path(route='agenda_paciente_rehab_create/<int:id>',view=AgendaPacienteRehabCreate.as_view(), name='agenda_paciente_rehab_create'),
    path(route='agenda_paciente_rehab_update/<int:id>',view=AgendaPacienteRehabUpdate.as_view(), name='agenda_paciente_rehab_update'),
    path(route='agenda_paciente_rehab_delete/<int:id>',view=AgendaRehabDelete.as_view(), name='agenda_paciente_rehab_delete'),
]

asistencia = [
    path(route='check_in_rehab/',view=CheckInRehab.as_view(), name='check_in_rehab'),
    path(route='check_in_rehab_error_dni/',view=CheckInRehabErrorDni.as_view(), name='check_in_error_dni'),
    path(route='check_in_error_agenda_activa/',view=CheckInRehabErrorAgendaActiva.as_view(), name='check_in_error_agenda_activa'),
    path(route='check_in_error_asistencia_registrada/',view=CheckInRehabErrorAsistenciaRegistrada.as_view(), name='check_in_error_asistencia_registrada'),
    path(route='check_in_error_dia_incorrecto/<int:id>',view=CheckInRehabErrorDiaIncorrecto.as_view(), name='check_in_error_dia_incorrecto'),
]

informes = [
    path(route='informes/<int:id>',view=InformesList.as_view(), name='informes'),
    path(route='informe_create/<int:id>',view=InformeCreate.as_view(), name='informe_create'),
    path(route='informe_detail/<int:id>',view=InformeDetail.as_view(), name='informe_detail'),
]

urlpatterns = inicio + pacientes + profesionales + rehabilitacion + alta + tipos_discapacidad + diagnosticos_etiologicos + diagnosticos_funcionales + tratamiento_profesional + agenda + asistencia + informes