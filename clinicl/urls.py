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
    path('login-signup/', views.login_signup_view, name='login-signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('save_user_info/', views.save_user_info, name='save_user_info'),
    path('send_reset_code/', views.send_reset_code, name='send_reset_code'),
    path('reset_password/', views.reset_password, name='reset_password/'),
    path('send_reset_code_login/', views.send_reset_code_login, name='send_reset_code_login'),
    path('reset_password_login/', views.reset_password_login, name='reset_password_login/'),
    path('attach-page/', views.attach_page, name='attach-page'),
    path('save_organization/', views.save_organization, name='save_organization'),
    path('profile_link/', views.profile_link, name='profile_link'),
    path('handle_image_upload/', views.handle_image_upload, name='handle_image_upload'),
    path('get-doctors/<str:clinic_ext_id>/', views.get_doctors_by_clinic, name='get-doctors-by-clinic'),
    path('appoint_doctor/', views.appoint_doctor, name='appoint_doctor'),
    path('update_doctor/', views.update_doctor, name='update_doctor'),
    path('find_user_view/', views.find_user_view, name='find_user_view'),
    path('create_appointment/', views.create_appointment, name='create_appointment'),
    path('medical_history/', views.medical_history, name='medical_history'),
    path('cancel-appointment/<int:appointment_id>', views.cancel_appointment, name='cancel-appointment'),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)