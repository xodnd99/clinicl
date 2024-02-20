from django.shortcuts import render
from rest_framework import generics
from clinicApp.models import UserProfile
from clinicApp.serializers import YourModelSerializer

def home(request):
    return render(request, 'html/index.html')


from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'


class YourModelList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = YourModelSerializer

