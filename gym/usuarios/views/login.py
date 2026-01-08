from django.contrib.auth import (
    login,
)

from django.shortcuts import redirect, render
from django.views import View
from usuarios.forms import LoginForm

from utils.permissions import es_admin_o_finanzas, es_admin_o_gimnasio, es_admin_o_rehabilitacion


class LoginView(View):

    def get(self, request):
        form = LoginForm()

        return render(
            request,
            'usuarios/login.html',
            dict(
                form=form
            )
        )
    
    def post(self, request):
        form = LoginForm(request.POST or None)
        if request.POST and form.is_valid():
            user = form.login(request)
            if user:
                permiso_gym = es_admin_o_gimnasio(user)
                permiso_fina = es_admin_o_finanzas(user)
                permiso_rehab = es_admin_o_rehabilitacion(user)
                if permiso_gym == True:
                    login(request, user)
                    return redirect ('inicio')
                elif permiso_fina == True:
                    login(request, user)
                    return redirect ('index')
                elif permiso_rehab == True:
                    login(request, user)
                    return redirect ('inicio_rehab')
                
        return render(
            request,
            'usuarios/login.html',
            dict(
                form=form,
            )
        )