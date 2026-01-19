from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from usuarios.forms import LoginForm
from utils.permissions import tiene_area, solo_areas
from utils.roles import COMBINACIONES_VALIDAS, AREAS


class LoginView(View):

    def get(self, request):
        return render(request, 'usuarios/login.html', {
            "form": LoginForm()
        })

    def post(self, request):
        form = LoginForm(request.POST or None)

        if form.is_valid():
            user = form.login(request)

            if not user:
                return render(request, 'usuarios/login.html', {"form": form})

            if not tiene_area(
                user,
                AREAS["GIMNASIO"],
                AREAS["REHAB"],
                AREAS["FINANZAS"],
            ):
                form.add_error(None, "No tiene permisos para acceder al sistema")
                return render(request, 'usuarios/login.html', {"form": form})

            login(request, user)

            if (
                solo_areas(user, COMBINACIONES_VALIDAS["gym_rehab"])
                and tiene_area(user, AREAS["GIMNASIO"], AREAS["REHAB"])
            ):
                return redirect("inicio")

            if solo_areas(user, COMBINACIONES_VALIDAS["gym"]):
                return redirect("inicio")

            if solo_areas(user, COMBINACIONES_VALIDAS["rehab"]):
                return redirect("inicio_rehab")

            if tiene_area(user, AREAS["FINANZAS"]):
                return redirect("index")

            form.add_error(None, "Configuración de permisos inválida")
        
        return render(request, 'usuarios/login.html', {"form": form})