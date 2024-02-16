from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='html/index.html'), name='home'),  # URL для отображения index.html
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
]
