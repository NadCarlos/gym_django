from django.urls import path

from usuarios.views.register import RegisterView
from usuarios.views.login import LoginView
from usuarios.views.logout import LogoutView


urlpatterns = [
    path(route='register/', view=RegisterView.as_view(), name='register'),
    path(route='login/', view=LoginView.as_view(), name='login'),
    path(route='logout/', view=LogoutView.as_view(), name='logout'),
]