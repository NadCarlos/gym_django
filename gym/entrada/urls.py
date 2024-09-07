from django.urls import path

from entrada.views.asistencia import (
    NuevaAsistenciaPaciente,
    AsistenciaPacienteList,
    CheckIn,
    CheckInConfirm,
    CheckInSuccess,
    CheckInError,
    CheckInNotFound,
    PrestacionNotFound,
)


urlpatterns = [
    path(route='<int:id>/nueva_asistencia_paciente/',view=NuevaAsistenciaPaciente.as_view(), name='nueva_asistencia_paciente'),
    path(route='<int:id>/historial_aistencias_paciente/',view=AsistenciaPacienteList.as_view(), name='historial_aistencias_paciente'),
    path(route='check_in/',view=CheckIn.as_view(), name='check_in'),
    path(route='<int:id>/check_in_confirm/',view=CheckInConfirm.as_view(), name='check_in_confirm'),
    path(route='<int:id>/check_in_success/',view=CheckInSuccess.as_view(), name='check_in_success'),
    path(route='check_in_error/',view=CheckInError.as_view(), name='check_in_error'),
    path(route='check_in_not_found/',view=CheckInNotFound.as_view(), name='check_in_not_found'),
    path(route='<int:id>/error_no_prestacion/',view=PrestacionNotFound.as_view(), name='error_no_prestacion'),
]