from django.urls import path

from rehabilitacion.views.inicio.index import(
    IndexView,
)


urlpatterns = [
    path(route='',view=IndexView.as_view(), name='inicio'),
]