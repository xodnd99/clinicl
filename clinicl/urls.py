from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from clinicApp.views import YourModelList, YourModelDetail

urlpatterns = [
    path('', TemplateView.as_view(template_name='html/index.html'), name='home'),  # URL для отображения index.html
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('api/yourmodels/', YourModelList.as_view(), name='yourmodel-list'),
    path('api/yourmodels/<int:pk>/', YourModelDetail.as_view(), name='yourmodel-detail'),
]
if settings.DEBUG:    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)