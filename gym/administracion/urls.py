from django.urls import path

from administracion.views.pacientes import (
    PacientesList,
    PacienteDetail,
    PacienteCreate,
    PacienteDelete,
    )

from administracion.views.prestacion_paciente import (
    NuevaPrestacionPaciente,
)


from administracion.views.obra_social import (
    ObraSocialList,
    ObraSocialCreate,
)

from administracion.views.prestacion import (
    PrestacionList,
    PrestacionCreate,
)


urlpatterns = [
    path(route='pacientes/',view=PacientesList.as_view(), name='pacientes_list'),    
    path(route='paciente_create/',view=PacienteCreate.as_view(), name='paciente_create'),
    path(route='<int:id>/paciente_detail/',view=PacienteDetail.as_view(), name='paciente_detail'),
    path(route='<int:id>/paciente_delete/',view=PacienteDelete.as_view(), name='paciente_delete'),

    path(route='<int:id>/nueva_prestacion_paciente/',view=NuevaPrestacionPaciente.as_view(), name='nueva_prestacion_paciente'),

    path(route='obras_sociales/',view=ObraSocialList.as_view(), name='obras_sociales'),
    path(route='obra_social_create/',view=ObraSocialCreate.as_view(), name='obra_social_create'),

    path(route='prestaciones/',view=PrestacionList.as_view(), name='prestaciones'),
    path(route='prestacion_create/',view=PrestacionCreate.as_view(), name='prestacion_create'),
]