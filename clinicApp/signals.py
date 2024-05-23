# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Prescription, Appointment, Attachment
from .utils import send_prescription_email, send_appointment_email, send_detach_email, send_appointment_completed_email

@receiver(post_save, sender=Prescription)
def send_prescription_notification(sender, instance, created, **kwargs):
    if created:
        send_prescription_email(instance.patient, instance.doctor, instance.pdf_file.path)

@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, created, **kwargs):
    if created:
        send_appointment_email(instance.patient, instance.doctor, instance.date_time)
    elif instance.status == 'completed':
        send_appointment_completed_email(instance.patient, instance.doctor)

@receiver(post_save, sender=Attachment)
def send_detach_notification(sender, instance, **kwargs):
    if not instance.active:
        send_detach_email(instance.patient, instance.doctor)
