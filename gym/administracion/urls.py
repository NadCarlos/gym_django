from django.urls import path

from administracion.views.pacientes import (
    PacientesList,
    PacienteDetail,
    PacienteCreate,
    PacienteUpdate,
    PacienteDelete,
    )

from administracion.views.prestacion_paciente import (
    NuevaPrestacionPaciente,
    ListPrestacionPaciente,
    ActiveError,
)

from administracion.views.obra_social import (
    ObraSocialList,
    ObraSocialCreate,
    ObraSocialUpdate,
    ObraSocialDelete,
)

from administracion.views.prestacion import (
    PrestacionList,
    PrestacionCreate,
    PrestacionUpdate,
    PrestacionDelete,
)

from administracion.views.asistencias import (
    AsistenciasList,
)


urlpatterns = [
    path(route='pacientes/',view=PacientesList.as_view(), name='pacientes_list'),    
    path(route='paciente_create/',view=PacienteCreate.as_view(), name='paciente_create'),
    path(route='<int:id>/paciente_detail/',view=PacienteDetail.as_view(), name='paciente_detail'),
    path(route='<int:id>/paciente_update/',view=PacienteUpdate.as_view(), name='paciente_update'),
    path(route='<int:id>/paciente_delete/',view=PacienteDelete.as_view(), name='paciente_delete'),

    path(route='<int:id>/nueva_prestacion_paciente/',view=NuevaPrestacionPaciente.as_view(), name='nueva_prestacion_paciente'),
    path(route='<int:id>/list_prestacion_paciente/',view=ListPrestacionPaciente.as_view(), name='list_prestacion_paciente'),
    path(route='active_error/',view=ActiveError.as_view(), name='active_error'),

    path(route='obras_sociales/',view=ObraSocialList.as_view(), name='obras_sociales'),
    path(route='obra_social_create/',view=ObraSocialCreate.as_view(), name='obra_social_create'),
    path(route='<int:id>/obra_social_update/',view=ObraSocialUpdate.as_view(), name='obra_social_update'),
    path(route='<int:id>/obra_social_delete/',view=ObraSocialDelete.as_view(), name='obra_social_delete'),

    path(route='prestaciones/',view=PrestacionList.as_view(), name='prestaciones'),
    path(route='prestacion_create/',view=PrestacionCreate.as_view(), name='prestacion_create'),
    path(route='<int:id>/prestacion_update/',view=PrestacionUpdate.as_view(), name='prestacion_update'),
    path(route='<int:id>/prestacion_delete/',view=PrestacionDelete.as_view(), name='prestacion_delete'),

    path(route='asistencias/',view=AsistenciasList.as_view(), name='asistencias'),
]