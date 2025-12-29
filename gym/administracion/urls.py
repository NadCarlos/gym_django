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
    PacienteCreateFromExistent,
    PacienteRedirectFromExistent,
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
    ProfesionalCreateFromExistent,
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
    TratamientosPorProfesionalView,
    ProfesionalesPorTratamientoView,
)

from administracion.views.agenda import(
    AgendaPaciente,
    AgendaProfesional,
    AgendaProfesionalToCsv,
    AgendaPacienteCreate,
    AgendaPacienteUpdate,
    AgendaDelete,
    ErrorPrestacionFaltante,
    ErrorHora,
)

from administracion.views.planes import(
    PlanesList,
    PlanCreate,
    PlanUpdate,
    PlanDelete,
)

from administracion.views.paciente_plan import(
    PacientePlanesList,
    PacientePlanCreate,
    PacientePlanDelete,
)

from administracion.views.cuota import(
    GenerateCuotas,
    CuotasList,
)

from administracion.views.pago import(
    PagoCreate,
    PagoList,
    PagoDelete,
)


pacientes = [
    path(route='pacientes/<state>',view=PacientesList.as_view(), name='pacientes_list'),
    path(route='pacientes_csv/<state>/<int:area>',view=PacientesToCsv.as_view(), name='pacientes_csv'),
    path(route='paciente_create/',view=PacienteCreate.as_view(), name='paciente_create'),
    path(route='<int:id>/paciente_detail/',view=PacienteDetail.as_view(), name='paciente_detail'),
    path(route='<int:id>/paciente_update/',view=PacienteUpdate.as_view(), name='paciente_update'),
    path(route='<int:id>/paciente_delete/',view=PacienteDelete.as_view(), name='paciente_delete'),
    path(route='<int:id>/paciente_reactivate/',view=PacienteReactivate.as_view(), name='paciente_reactivate'),
    path(route='error_paciente_existente/',view=ErrorPacienteExistente.as_view(), name='error_paciente_existente'),
    path(route='paciente_create_existente/',view=PacienteCreateFromExistent.as_view(), name='paciente_create_from_existent'),
    path(route='paciente_redirect_existente/',view=PacienteRedirectFromExistent.as_view(), name='paciente_redirect_existente'),
]

prestacion_paciente = [
    path(route='<int:id>/nueva_prestacion_paciente/',view=NuevaPrestacionPaciente.as_view(), name='nueva_prestacion_paciente'),
    path(route='<int:id>/list_prestacion_paciente/',view=ListPrestacionPaciente.as_view(), name='list_prestacion_paciente'),
    path(route='<int:id>/update_prestacion_paciente/',view=PrestacionPacienteUpdate.as_view(), name='update_prestacion_paciente'),
    path(route='<int:id>/delete_prestacion_paciente/',view=DeletePrestacionPaciente.as_view(), name='delete_prestacion_paciente'),
    path(route='active_error/',view=ActiveError.as_view(), name='active_error'),
]

obra_social = [
    path(route='obras_sociales/<int:area>',view=ObraSocialList.as_view(), name='obras_sociales'),
    path(route='obra_social_create/<int:area>',view=ObraSocialCreate.as_view(), name='obra_social_create'),
    path(route='<int:id>/obra_social_update/<int:area>',view=ObraSocialUpdate.as_view(), name='obra_social_update'),
    path(route='<int:id>/obra_social_delete/<int:area>',view=ObraSocialDelete.as_view(), name='obra_social_delete'),
]

prestaciones = [
    path(route='prestaciones/<int:area>',view=PrestacionList.as_view(), name='prestaciones'),
    path(route='prestacion_create/<int:area>',view=PrestacionCreate.as_view(), name='prestacion_create'),
    path(route='<int:id>/prestacion_update/<int:area>',view=PrestacionUpdate.as_view(), name='prestacion_update'),
    path(route='<int:id>/prestacion_delete/<int:area>',view=PrestacionDelete.as_view(), name='prestacion_delete'),
]

asistencias = [
    path(route='asistencias/',view=AsistenciasList.as_view(), name='asistencias'),
    path(route='asistencias_csv/',view=AsistenciasToCsv.as_view(), name='asistencias_csv'),
]

profesional = [
    path(route='profesional_list/',view=ProfesionalList.as_view(), name='profesional_list'),
    path(route='profesional_create/',view=ProfesionalCreate.as_view(), name='profesional_create'),
    path(route='profesional_csv/<int:area>',view=ProfesionalesToCsv.as_view(), name='profesional_csv'),
    path(route='<int:id>/profesional_detail/',view=ProfesionalDetail.as_view(), name='profesional_detail'),
    path(route='<int:id>/profesional_update/',view=ProfesionalUpdate.as_view(), name='profesional_update'),
    path(route='<int:id>/profesional_delete/',view=ProfesionalDelete.as_view(), name='profesional_delete'),
    path(route='<error_profesional_existente/',view=ErrorProfesionalExistente.as_view(), name='error_profesional_existente'),
    path(route='profesional_create_existente/',view=ProfesionalCreateFromExistent.as_view(), name='profesional_create_from_existent'),
]

tratamientos = [
    path(route='tratamientos/<int:area>',view=TratamientoList.as_view(), name='tratamientos'),
    path(route='tratamiento_create/<int:area>',view=TratamientoCreate.as_view(), name='tratamiento_create'),
    path(route='tratamiento_update/<int:id>/<int:area>',view=TratamientoUpdate.as_view(), name='tratamiento_update'),
    path(route='tratamiento_delete/<int:id>/<int:area>',view=TratamientoDelete.as_view(), name='tratamiento_delete'),
]

tratamiento_profesional = [
    path(route='<int:id>/tratamiento_profesional_list/',view=TratamientoProfesionalList.as_view(), name='tratamiento_profesional_list'),
    path(route='<int:id>/tratamiento_profesional_create/',view=TratamientoProfesionalCreate.as_view(), name='tratamiento_profesional_create'),
    path(route='<int:id>/tratamiento_profesional_delete/',view=TratamientoProfesionalDelete.as_view(), name='tratamiento_profesional_delete'),
    path(route='tratamientos/<int:profesional_id>/',view=TratamientosPorProfesionalView.as_view(), name='tratamientos_por_profesional'),
    path(route='tratamientos_p/<int:id_tratamiento>/',view=ProfesionalesPorTratamientoView.as_view(), name='profesionales_por_tratamiento'),
]

agenda = [
    path(route='<int:id>/agenda_paciente',view=AgendaPaciente.as_view(), name='agenda_paciente'),
    path(route='<int:id>/agenda_profesional',view=AgendaProfesional.as_view(), name='agenda_profesional'),
    path(route='<int:id>/agenda_profesional_csv',view=AgendaProfesionalToCsv.as_view(), name='agenda_profesional_csv'),
    path(route='<int:id>/agenda_paciente_create',view=AgendaPacienteCreate.as_view(), name='agenda_paciente_create'),
    path(route='<int:id>/agenda_paciente_update',view=AgendaPacienteUpdate.as_view(), name='agenda_paciente_update'),
    path(route='<int:id>/agenda_paciente_delete',view=AgendaDelete.as_view(), name='agenda_paciente_delete'),
    path(route='error_prestacion_paciente',view=ErrorPrestacionFaltante.as_view(), name='error_prestacion_paciente'),
    path(route='error_hora',view=ErrorHora.as_view(), name='error_hora'),
]

planes = [
    path(route='planes_list/',view=PlanesList.as_view(), name='planes_list'),
    path(route='plan_create/',view=PlanCreate.as_view(), name='plan_create'),
    path(route='<int:id>/plan_update/',view=PlanUpdate.as_view(), name='plan_update'),
    path(route='<int:id>/plan_delete',view=PlanDelete.as_view(), name='plan_delete'),
]

paciente_plan = [
    path(route='<int:id>/paciente_plan_create/',view=PacientePlanCreate.as_view(), name='paciente_plan_create'),
    path(route='<int:id>/paciente_plan_list/',view=PacientePlanesList.as_view(), name='paciente_plan_list'),
    path(route='<int:id>/paciente_plan_delete',view=PacientePlanDelete.as_view(), name='paciente_plan_delete'),
]

cuotas = [
    path(route='generate_cuotas/',view=GenerateCuotas.as_view(), name='generate_cuotas'),
    path(route='cuotas_list/<state>',view=CuotasList.as_view(), name='cuotas_list'),
]

pagos = [
    path(route='<int:id>/<int:id_c>/pago_create/',view=PagoCreate.as_view(), name='pago_create'),
    path(route='<int:id>/pago_list/',view=PagoList.as_view(), name='pago_list'),
    path(route='<int:id>/pago_delete/',view=PagoDelete.as_view(), name='pago_delete'),
]

urlpatterns = pacientes + prestacion_paciente + obra_social + prestaciones + asistencias + profesional + tratamientos + tratamiento_profesional + agenda + planes + paciente_plan + cuotas + pagos