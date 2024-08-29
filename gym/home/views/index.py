from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

class IndexView(View):

    @method_decorator(login_required(login_url='login'))
    def get(self, request):
        return render(
            request,
            'home/index.html'
        )
    

class ErrorView(View):

    def get(self, request):
        return render(
            request,
            'home/error.html'
        )