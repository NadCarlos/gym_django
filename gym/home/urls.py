from django.urls import path

from home.views.index import (
    IndexView,
    ErrorView
)


urlpatterns = [
    path(route='',view=IndexView.as_view(), name='inicio'),
    path(route='error/',view=ErrorView.as_view(), name='error'),
]