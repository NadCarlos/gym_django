from django.urls import path

from rehabilitacion.views.inicio.index import(
    IndexView,
)

from rehabilitacion.views.pacientes_rehab import(
    PacientesRehabList,
    PacienteRehabDetail,
    PacienteRehabCreate,
    PacienteRehabCreateFromExistent,
    PacienteRehabUpdate,
)

from rehabilitacion.views.profesional_rehab import(
    ProfesionalRehabList,
    ProfesionalRehabDetail,
    ProfesionalRehabCreate,
    ProfesionalRehabCreateFromExistent,
)

from rehabilitacion.views.rehabilitacion import(
    RehabilitacionCreate,
    RehabilitacionUpdate,
)

from rehabilitacion.views.alta import(
    AltaCreate,
    DiagnosticosByFamiliaView,
    AltaDetail,
)


inicio = [
    path(route='',view=IndexView.as_view(), name='inicio_rehab'),
]

pacientes = [
    path(route='pacientes/list/<state>',view=PacientesRehabList.as_view(), name='pacientes_rehab_list'),
    path(route='pacientes/detail/<int:id>',view=PacienteRehabDetail.as_view(), name='paciente_rehab_detail'),
    path(route='pacientes/create',view=PacienteRehabCreate.as_view(), name='paciente_rehab_create'),
    path(route='pacientes/create_from_existent',view=PacienteRehabCreateFromExistent.as_view(), name='paciente_rehab_create_from_existent'),
    path(route='pacientes/update/<int:id>',view=PacienteRehabUpdate.as_view(), name='paciente_rehab_update'),
]

profesionales = [
    path(route='profesionales/list',view=ProfesionalRehabList.as_view(), name='profesional_rehab_list'),
    path(route='profesionales/detail/<int:id>',view=ProfesionalRehabDetail.as_view(), name='profesional_rehab_detail'),
    path(route='profesionales/create',view=ProfesionalRehabCreate.as_view(), name='profesional_rehab_create'),
    path(route='profesional/create_from_existent',view=ProfesionalRehabCreateFromExistent.as_view(), name='profesional_rehab_create_from_existent'),
]

rehabilitacion = [
    path(route='rehabilitacion/create/<int:id>',view=RehabilitacionCreate.as_view(), name='rehab_create'),
    path(route='rehabilitacion/update/<int:id>',view=RehabilitacionUpdate.as_view(), name='rehab_update'),
]

alta = [
    path(route='alta/create/<int:id>',view=AltaCreate.as_view(), name='alta_create'),
    path(route="diagnosticos/<int:familia_id>/", view=DiagnosticosByFamiliaView.as_view(), name="get_diagnosticos_by_familia"),
    path(route='alta/detail/<int:id>',view=AltaDetail.as_view(), name='alta_detail'),
]

urlpatterns = inicio + pacientes + profesionales + rehabilitacion + alta