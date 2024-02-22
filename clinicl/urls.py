from django.urls import path
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from clinicApp.views import YourModelList, YourModelDetail
from .views import CustomLoginView
from .views import YourRegistrationView
from . import views
urlpatterns = [
    path('', TemplateView.as_view(template_name='html/index.html'), name='home'),  # URL для отображения index.html
    path('login/', CustomLoginView.as_view(), name='login'),
    path('admin/', admin.site.urls),
    path('api/yourmodels/', YourModelList.as_view(), name='yourmodel-list'),
    path('api/yourmodels/<int:pk>/', YourModelDetail.as_view(), name='yourmodel-detail'),
    path('registration/', YourRegistrationView.as_view(), name='registration'),
    path('registration/login.html', views.login_page_view, name='login_page'),
    path('html/index.html', TemplateView.as_view(template_name='html/index.html'), name='index'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)