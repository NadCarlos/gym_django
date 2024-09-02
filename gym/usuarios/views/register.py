from django.contrib.auth import (
    login,
)
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.views import View
from usuarios.forms import UserRegisterForm


class RegisterView(View):

    @method_decorator(permission_required(perm='gym.register', login_url='login'))
    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        form = UserRegisterForm()

        return render(
            request,
            'usuarios/register.html',
            dict(
                form=form
            )
        )
    
    @method_decorator(permission_required(perm='gym.register', login_url='login'))
    @method_decorator(login_required(login_url='login'))
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