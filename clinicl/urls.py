from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from clinicApp import views
from .views import HomeView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('login-signup/', views.login_signup_view, name='login-signup'),  # Уникальный URL-адрес для регистрации
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)