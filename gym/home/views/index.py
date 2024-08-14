from django.shortcuts import render
from django.views import View


class IndexView(View):

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