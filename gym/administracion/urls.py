from django.urls import path

from administracion.views.pacientes import (
    PacientesList,
    PacienteDetail,
    PacienteCreate,
    PacienteUpdate,
    PacienteDelete,
    PacientesToCsv,
    ErrorPacienteExistente,
    PacienteReactivate,
    )

from administracion.views.prestacion_paciente import (
    NuevaPrestacionPaciente,
    ListPrestacionPaciente,
    ActiveError,
    DeletePrestacionPaciente,
    PrestacionPacienteUpdate,
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
    AsistenciasToCsv,
)

from administracion.views.profesional import (
    ProfesionalList,
    ProfesionalDetail,
    ProfesionalDelete,
    ProfesionalCreate,
    ProfesionalUpdate,
    ProfesionalesToCsv,
    ErrorProfesionalExistente,
)

from administracion.views.tratamiento import (
    TratamientoList,
    TratamientoCreate,
    TratamientoUpdate,
    TratamientoDelete,
)

from administracion.views.tratamiento_profesional import (
    TratamientoProfesionalList,
    TratamientoProfesionalCreate,
    TratamientoProfesionalDelete,
)

from administracion.views.agenda import(
    AgendaPaciente,
    AgendaProfesional,
    AgendaPacienteCreate,
    ErrorPrestacionFaltante,
    ErrorHora,
)


pacientes = [
    path(route='pacientes/<state>',view=PacientesList.as_view(), name='pacientes_list'),
    path(route='pacientes_csv/',view=PacientesToCsv.as_view(), name='pacientes_csv'),
    path(route='paciente_create/',view=PacienteCreate.as_view(), name='paciente_create'),
    path(route='<int:id>/paciente_detail/',view=PacienteDetail.as_view(), name='paciente_detail'),
    path(route='<int:id>/paciente_update/',view=PacienteUpdate.as_view(), name='paciente_update'),
    path(route='<int:id>/paciente_delete/',view=PacienteDelete.as_view(), name='paciente_delete'),
    path(route='<int:id>/paciente_reactivate/',view=PacienteReactivate.as_view(), name='paciente_reactivate'),
    path(route='error_paciente_existente/',view=ErrorPacienteExistente.as_view(), name='error_paciente_existente'),
]

prestacion_paciente = [
    path(route='<int:id>/nueva_prestacion_paciente/',view=NuevaPrestacionPaciente.as_view(), name='nueva_prestacion_paciente'),
    path(route='<int:id>/list_prestacion_paciente/',view=ListPrestacionPaciente.as_view(), name='list_prestacion_paciente'),
    path(route='<int:id>/update_prestacion_paciente/',view=PrestacionPacienteUpdate.as_view(), name='update_prestacion_paciente'),
    path(route='<int:id>/delete_prestacion_paciente/',view=DeletePrestacionPaciente.as_view(), name='delete_prestacion_paciente'),
    path(route='active_error/',view=ActiveError.as_view(), name='active_error'),
]

obra_social = [
    path(route='obras_sociales/',view=ObraSocialList.as_view(), name='obras_sociales'),
    path(route='obra_social_create/',view=ObraSocialCreate.as_view(), name='obra_social_create'),
    path(route='<int:id>/obra_social_update/',view=ObraSocialUpdate.as_view(), name='obra_social_update'),
    path(route='<int:id>/obra_social_delete/',view=ObraSocialDelete.as_view(), name='obra_social_delete'),
]

prestaciones = [
    path(route='prestaciones/',view=PrestacionList.as_view(), name='prestaciones'),
    path(route='prestacion_create/',view=PrestacionCreate.as_view(), name='prestacion_create'),
    path(route='<int:id>/prestacion_update/',view=PrestacionUpdate.as_view(), name='prestacion_update'),
    path(route='<int:id>/prestacion_delete/',view=PrestacionDelete.as_view(), name='prestacion_delete'),
]

asistencias = [
    path(route='asistencias/',view=AsistenciasList.as_view(), name='asistencias'),
    path(route='asistencias_csv/',view=AsistenciasToCsv.as_view(), name='asistencias_csv'),
]

profesional = [
    path(route='profesional_list/',view=ProfesionalList.as_view(), name='profesional_list'),
    path(route='profesional_create/',view=ProfesionalCreate.as_view(), name='profesional_create'),
    path(route='profesional_csv/',view=ProfesionalesToCsv.as_view(), name='profesional_csv'),
    path(route='<int:id>/profesional_detail/',view=ProfesionalDetail.as_view(), name='profesional_detail'),
    path(route='<int:id>/profesional_update/',view=ProfesionalUpdate.as_view(), name='profesional_update'),
    path(route='<int:id>/profesional_delete/',view=ProfesionalDelete.as_view(), name='profesional_delete'),
    path(route='<error_profesional_existente/',view=ErrorProfesionalExistente.as_view(), name='error_profesional_existente'),
]

tratamientos = [
    path(route='tratamientos/',view=TratamientoList.as_view(), name='tratamientos'),
    path(route='tratamiento_create/',view=TratamientoCreate.as_view(), name='tratamiento_create'),
    path(route='<int:id>/tratamiento_update/',view=TratamientoUpdate.as_view(), name='tratamiento_update'),
    path(route='<int:id>/tratamiento_delete/',view=TratamientoDelete.as_view(), name='tratamiento_delete'),
]

tratamiento_profesional = [
    path(route='<int:id>/tratamiento_profesional_list/',view=TratamientoProfesionalList.as_view(), name='tratamiento_profesional_list'),
    path(route='<int:id>/tratamiento_profesional_create/',view=TratamientoProfesionalCreate.as_view(), name='tratamiento_profesional_create'),
    path(route='<int:id>/tratamiento_profesional_delete/',view=TratamientoProfesionalDelete.as_view(), name='tratamiento_profesional_delete'),
]

agenda = [
    path(route='<int:id>/agenda_paciente',view=AgendaPaciente.as_view(), name='agenda_paciente'),
    path(route='<int:id>/agenda_profesional',view=AgendaProfesional.as_view(), name='agenda_profesional'),
    path(route='<int:id>/agenda_paciente_create',view=AgendaPacienteCreate.as_view(), name='agenda_paciente_create'),
    path(route='error_prestacion_paciente',view=ErrorPrestacionFaltante.as_view(), name='error_prestacion_paciente'),
    path(route='error_hora',view=ErrorHora.as_view(), name='error_hora'),
]
urlpatterns = pacientes + prestacion_paciente + obra_social + prestaciones + asistencias + profesional + tratamientos + tratamiento_profesional + agenda