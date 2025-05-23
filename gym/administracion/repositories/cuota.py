from typing import List, Optional

from administracion.models import Cuota, PacientePlan


class CuotaRepository:

    def get_all(self) -> List[Cuota]:
        return Cuota.objects.all().order_by("id_paciente_plan__id_paciente__apellido")
    
    def get_by_id(self, id: int) -> Optional[Cuota]:
        return Cuota.objects.get(id=id)
    
    def filter_by_id(self, id) -> Optional[Cuota]:
        return Cuota.objects.filter(id=id)
    
    def filter_by_paciente_id(self, id) -> Optional[Cuota]:
        return Cuota.objects.filter(id_paciente_plan__id_paciente__id=id)
    
    def filter_by_paciente_id_mes(self,id_paciente, year, month) -> List[Cuota]:
        return Cuota.objects.filter(id_paciente_plan__id_paciente__id=id_paciente).filter(imputado__year=year, imputado__month=month).first()
    
    def filter_by_anulado(self, state) -> List[Cuota]:
        return Cuota.objects.filter(anulado=state).order_by('id_paciente_plan__id_paciente__apellido')
    
    def filter_by_anulado_dates(self, state, start_date, end_date) -> Optional[Cuota]:
        return Cuota.objects.filter(anulado=state, imputado__gte=start_date, imputado__lt=end_date).order_by('id_paciente_plan__id_paciente__apellido')
    
    def cuota_exist(self,id_paciente, year, month) -> List[Cuota]:
        return Cuota.objects.filter(id_paciente_plan__id_paciente__id=id_paciente).filter(imputado__year=year, imputado__month=month).exists()
    
    def delete_by_activo(self, cuota: Cuota):
        cuota.anulado=True
        cuota.save()
    
    def create(
        self,
        imputado: str,
        id_paciente_plan: PacientePlan,
        valor: float,
    ):
        return Cuota.objects.create(
            imputado=imputado,
            id_paciente_plan=id_paciente_plan,
            valor=valor,
        )
    
    def update_anulado(
        self, 
        cuota: Cuota,
        anulado: bool,
    ) -> Cuota:

        cuota.anulado = anulado

        cuota.save()
