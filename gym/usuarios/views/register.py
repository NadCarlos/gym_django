from django.contrib.auth import (
    login,
)

from django.shortcuts import redirect, render
from django.views import View
from usuarios.forms import UserRegisterForm


class RegisterView(View):

    def get(self, request):
        form = UserRegisterForm()

        return render(
            request,
            'usuarios/register.html',
            dict(
                form=form
            )
        )
    
    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect ('inicio')
        
        return render(
            request,
            'usuarios/register.html',
            dict(
                form=form
            )
        )