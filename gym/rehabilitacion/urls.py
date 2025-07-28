from django.urls import path

from rehabilitacion.views.inicio.index import(
    IndexView,
)

from rehabilitacion.views.pacientes_rehab import(
    PacientesRehabList,
    PacienteRehabDetail,
    PacienteRehabCreate,
    PacienteRehabCreateFromExistent,
)


inicio = [
    path(route='',view=IndexView.as_view(), name='inicio_rehab'),
]

pacientes = [
    path(route='pacientes/list/<state>',view=PacientesRehabList.as_view(), name='pacientes_rehab_list'),
    path(route='pacientes/detail/<int:id>',view=PacienteRehabDetail.as_view(), name='paciente_rehab_detail'),
    path(route='pacientes/create',view=PacienteRehabCreate.as_view(), name='paciente_rehab_create'),
    path(route='pacientes/create_from_existent',view=PacienteRehabCreateFromExistent.as_view(), name='paciente_create_from_existent'),
]

urlpatterns = inicio + pacientes