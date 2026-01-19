from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from utils.decorators import requiere_areas


@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class IndexView(View):

    def get(self, request):
        return render(
            request,
            'inicio/index.html'
        )
    

@method_decorator(login_required(login_url='login'), name='dispatch')
@method_decorator(requiere_areas("Rehabilitacion"), name="dispatch")
class DiagnosticosIndex(View):

    def get(self, request):
        return render(
            request,
            'inicio/diagnosticos_index.html'
        )