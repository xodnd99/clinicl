from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='html/index.html'), name='home'),  # URL для отображения index.html
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
]
if settings.DEBUG:    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)