from django.contrib.auth import (
    login,
)

from django.shortcuts import redirect, render
from django.views import View
from usuarios.forms import LoginForm


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
                login(request, user)
                return redirect ('inicio')
        return render(
            request,
            'usuarios/login.html',
            dict(
                form=form,
            )
        )