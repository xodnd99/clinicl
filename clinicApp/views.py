from rest_framework import generics
from .models import UserProfile
from .serializers import YourModelSerializer

class YourModelList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = YourModelSerializer

class YourModelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = YourModelSerializer
