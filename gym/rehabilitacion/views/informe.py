from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from utils.decorators import requiere_areas

from rehabilitacion.forms import(
    InformeCreateForm,
    ArchivoCreateForm,
    LinkCreateForm,
)

from rehabilitacion.repositories.informe import InformeRepository
from rehabilitacion.repositories.archivo import ArchivoRepository
from rehabilitacion.repositories.link import LinkRepository
from administracion.repositories.paciente import PacienteRepository


informeRepo = InformeRepository()
archivoRepo = ArchivoRepository()
linkRepo = LinkRepository()
pacienteRepo = PacienteRepository()


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformesList(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        informes = informeRepo.filter_by_paciente_id(paciente_id=id)
        return render(
            request,
            'informes/list.html',
            dict(
                paciente=paciente,
                informes=informes,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeCreate(View):

    def get(self, request, id):
        paciente = pacienteRepo.get_by_id(id=id)
        form = InformeCreateForm(initial = {
            'id_paciente': paciente,
            }
        )
        return render(
            request,
            'informes/create.html',
            dict(
                paciente=paciente,
                form=form,
            )
        )

    def post(self, request, id):
        form = InformeCreateForm(request.POST)
        if form.is_valid():
            nuevo_informe = informeRepo.create(
                fecha=form.cleaned_data['fecha'],
                id_profesional=form.cleaned_data['id_profesional'],
                id_paciente=form.cleaned_data['id_paciente'],
                observaciones=form.cleaned_data['observaciones'],
            )
        return redirect('informe_detail', nuevo_informe.id)
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeUpdate(View):

    def get(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        form = InformeCreateForm(instance=informe)
        return render(
            request,
            'informes/update.html',
            dict(
                informe=informe,
                paciente=informe.id_paciente,
                form=form,
            )
        )

    def post(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        form = InformeCreateForm(request.POST, instance=informe)
        if form.is_valid():
            informe_actualizado = form.save()
            return redirect('informe_detail', informe_actualizado.id)
        return render(
            request,
            'informes/update.html',
            dict(
                informe=informe,
                paciente=informe.id_paciente,
                form=form,
            )
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeDetail(View):

    def get(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        archivos = archivoRepo.filter_by_informe_id(informe_id=informe.id)
        links = linkRepo.filter_by_informe_id(informe_id=informe.id)
        return render(
            request,
            'informes/detail.html',
            dict(
                informe=informe,
                archivos=archivos,
                links=links,
            )
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class InformeDelete(View):

    def get(self, request, id):
        informe = informeRepo.get_by_id(id=id)
        paciente_id = informe.id_paciente.id
        informeRepo.delete(informe=informe)
        return redirect('informes', paciente_id)


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class ArchivoCreate(View):

    def get(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        form = ArchivoCreateForm(initial = {
            'id_informe': informe.id,
            }
        )
        return render(
            request,
            'informes/archivo/create.html',
            dict(
                informe=informe,
                form=form,
            )
        )

    def post(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        archivos = request.FILES.getlist('archivo')
        for archivo in archivos:
            archivoRepo.create(
                archivo=archivo,
                id_informe=informe,
            )
        if archivos:
            return redirect('informe_detail', id=id)
        form = ArchivoCreateForm(initial={'id_informe': informe.id})
        return render(
            request,
            'informes/archivo/create.html',
            dict(
                informe=informe,
                form=form,
                error_archivo='Debes seleccionar al menos un archivo.',
            ),
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class ArchivoDelete(View):

    def get(self, request, id_archivo, id_informe):
        archivo = archivoRepo.get_by_id(id=id_archivo)
        archivoRepo.delete(archivo=archivo)
        return redirect('informe_detail', id_informe )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class LinkCreate(View):

    def get(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        if not informe:
            return redirect('inicio_rehab')
        form = LinkCreateForm(initial = {
            'id_informe': informe.id,
            }
        )
        return render(
            request,
            'informes/link/create.html',
            dict(
                informe=informe,
                form=form,
            )
        )

    def post(self, request, id):
        informe = informeRepo.filter_by_id(id=id)
        form = LinkCreateForm(request.POST)
        if form.is_valid():
            linkRepo.create(
                nombre=form.cleaned_data['nombre'],
                url=form.cleaned_data['url'],
                id_informe=form.cleaned_data['id_informe'],
            )
            return redirect('informe_detail', informe.id )


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class LinkDelete(View):

    def get(self, request, id_link, id_informe):
        link = linkRepo.get_by_id(id=id_link)
        linkRepo.delete(link=link)
        return redirect('informe_detail', id_informe )