import pandas as pd
import io

from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse

from administracion.models import Profesional

from administracion.filters import ProfesionalFilter

from administracion.forms import (
    ProfesionalCreateForm,
    ProfesionalUpdateForm,
    )

from administracion.repositories.profesional import ProfesionalRepository
from administracion.repositories.sexo import SexoRepository
from administracion.repositories.localidad import LocalidadRepository

profesionalRepo = ProfesionalRepository()
sexoRepo = SexoRepository()
localidadRepo = LocalidadRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalList(View):
    template_name = 'profesional/list.html'
    context_object_name = 'profesional'

    def get(self, request):

        filterset = ProfesionalFilter(request.GET, profesionalRepo.filter_by_activo())
        
        # Obtener el parámetro de ordenamiento
        ordering = request.GET.get('ordering', 'apellido')

        # Obtener el queryset filtrado
        profesionales = filterset.qs

        # Si existe un campo de ordenamiento, aplicarlo
        if ordering:
            profesionales = filterset.qs.order_by(ordering)

        return render(
            request,
            self.template_name,
            dict(
                profesionales=profesionales,
                form=filterset.form,
                ordering=ordering,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalesToCsv(View):

    def get(self, request):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=profesionales.xlsx'
       
        apellido = request.GET.get('apellido')
        id_sexo = request.GET.get('id_sexo')

        profesionales = Profesional.objects.filter(activo=True)

        if apellido:
            profesionales = profesionales.filter(apellido__icontains=apellido)

        if id_sexo:
            profesionales = profesionales.filter(id_sexo=id_sexo)

        data = []
        for profesional in profesionales:
            data.append([
                profesional.nombre,
                profesional.apellido,
                profesional.numero_dni,
                profesional.matricula,
                profesional.direccion,
                profesional.celular,
                profesional.fecha_nacimiento,
                profesional.id_localidad.nombre,
                profesional.id_sexo.nombre,
                ])

        df = pd.DataFrame(data, columns=[
            'Nombre',
            'Apellido',
            'Dni',
            'Matricula',
            'Direccion',
            'Celular',
            'Fecha de nacimiento',
            'localidad',
            'sexo',
            ])

        # Use an in-memory output stream to avoid file system I/O
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Profesionales', index=False)

        response.write(output.getvalue())

        return response


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalDetail(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        return render(
            request,
            'profesional/detail.html',
            dict(
                profesional=profesional,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalCreate(View):

    def get(self, request):
        sexo = sexoRepo.get_by_name(nombre="Masculino")
        localidad = localidadRepo.get_by_name(nombre="Rio Cuarto")
        form = ProfesionalCreateForm(initial = {
            'id_usuario': request.user,
            'id_sexo': sexo.id,
            'id_localidad': localidad.id
            }
        )
        return render(
            request,
            'profesional/create.html',
            dict(
                form=form
            )
        )

    def post(self, request):
        form = ProfesionalCreateForm(request.POST)
        try:
            if form.is_valid():
                dni = form.cleaned_data['numero_dni']
                dni=int(dni)
                dniExistente = profesionalRepo.filter_by_dni(numero_dni=dni)
                matricula = form.cleaned_data['matricula']
                matriculaExistente = profesionalRepo.filter_by_matricula(matricula=matricula)
                if dniExistente is None and matriculaExistente is None:
                    nombre = form.cleaned_data['nombre']
                    nombre = nombre.upper()
                    apellido = form.cleaned_data['apellido']
                    apellido = apellido.upper()
                    profesional_nuevo = profesionalRepo.create(
                        id_usuario=form.cleaned_data['id_usuario'],
                        nombre=nombre,
                        apellido=apellido,
                        numero_dni=form.cleaned_data['numero_dni'],
                        matricula=form.cleaned_data['matricula'],
                        fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                        id_sexo=form.cleaned_data['id_sexo'],
                        id_localidad=form.cleaned_data['id_localidad'],
                        direccion=form.cleaned_data['direccion'],
                        celular=form.cleaned_data['celular'],
                        )
                    return redirect('profesional_detail', profesional_nuevo.id)
                else:
                    return redirect('error_profesional_existente')
        except:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalUpdate(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        form = ProfesionalUpdateForm(instance=profesional)
        return render(
            request,
            'profesional/update.html',
            dict(
                form=form,
                profesional=profesional,
            )
        )

    def post(self, request, id):
        form = ProfesionalUpdateForm(request.POST)
        profesional = profesionalRepo.get_by_id(id=id)
        try:
            if form.is_valid():
                nombre = form.cleaned_data['nombre']
                nombre = nombre.upper()
                apellido = form.cleaned_data['apellido']
                apellido = apellido.upper()
                profesionalRepo.update(
                    profesional=profesional,
                    nombre=nombre,
                    apellido=apellido,
                    numero_dni=form.cleaned_data['numero_dni'],
                    matricula=form.cleaned_data['matricula'],
                    fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                    sexo=form.cleaned_data['id_sexo'],
                    localidad=form.cleaned_data['id_localidad'],
                    direccion=form.cleaned_data['direccion'],
                    celular=form.cleaned_data['celular'],
                    )
                return redirect('profesional_detail', profesional.id)
        except:
            return redirect('error')


@method_decorator(login_required(login_url='login'), name='dispatch')
class ProfesionalDelete(View):

    def get(self, request, id):
        profesional = profesionalRepo.get_by_id(id=id)
        #No elimino, cambio el campo activo a False
        profesionalRepo.delete_by_activo(profesional=profesional)
        return redirect('profesional_list')
    

@method_decorator(login_required(login_url='login'), name='dispatch')
class ErrorProfesionalExistente(View):

    def get(self, request):
        return render(
            request,
            'profesional/error_profesional_existente.html',
        )