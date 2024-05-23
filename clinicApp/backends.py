from django.contrib.auth.backends import BaseBackend
from .models import Patient, Doctor

class PatientBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            patient = Patient.objects.get(iin=username)
            if patient.check_password(password):
                return patient
        except Patient.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Patient.objects.get(pk=user_id)
        except Patient.DoesNotExist:
            return None

class DoctorBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            doctor = Doctor.objects.get(iin=username)
            if doctor.check_password(password):
                return doctor
        except Doctor.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Doctor.objects.get(pk=user_id)
        except Doctor.DoesNotExist:
            return None



