from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

class PatientManager(BaseUserManager):
    def create_user(self, iin, email, password=None, **extra_fields):
        if not iin:
            raise ValueError('The given IIN must be set')
        email = self.normalize_email(email)
        user = self.model(iin=iin, email=email, **extra_fields)
        user.set_password(password)  # Устанавливает и хэширует пароль
        user.save(using=self._db)  # Сохраняет пользователя
        return user

    def create_superuser(self, iin, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(iin, email, password, **extra_fields)

class Patient(AbstractBaseUser, PermissionsMixin):
    iin = models.CharField(_('IIN'), unique=True, primary_key=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    reset_code = models.CharField(max_length=5, blank=True, null=True)
    reset_code_created_at = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos', blank=True, null=True)
    objects = PatientManager()

    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = ['email']


    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def __str__(self):
        return str(self.iin)



    groups = models.ManyToManyField(
        verbose_name=_('groups'),
        to='auth.Group',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="patient_set",
        related_query_name="patient",
    )

    user_permissions = models.ManyToManyField(
        verbose_name=_('user permissions'),
        to='auth.Permission',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="patient_set",
        related_query_name="patient",
    )


from django.utils.html import mark_safe

class PatientDetail(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, to_field='iin', related_name='details')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to='patient_images/', null=True, blank=True)


    def get_initials(self):
        if self.patient:
            return f"{self.patient.first_name[0].upper()}{self.patient.last_name[0].upper()}"
        return ""

    def profile_pic_tag(self):
        if self.profile_pic:
            return mark_safe('<img src="%s" width="180" height="180" />' % self.profile_pic.url)
        else:
            return self.get_initials()

    def __str__(self):
        return f'Details for {self.patient.first_name} {self.patient.last_name}'



from django.db import models

class Organization(models.Model):
    ext_id = models.CharField(max_length=255, primary_key=True)
    name = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=1024, blank=True, null=True)
    phone_numbers = models.TextField(blank=True, null=True)
    hours_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


from django.db import models

from django.db import models
import datetime

class Doctor(models.Model):
    DAYS_OF_WEEK = (
        ('Пон', 'Monday'),
        ('Вто', 'Tuesday'),
        ('Сре', 'Wednesday'),
        ('Чет', 'Thursday'),
        ('Пят', 'Friday'),
        ('Суб', 'Saturday'),
        ('Вос', 'Sunday'),
    )
    iin = models.CharField(max_length=12, primary_key=True)
    full_name = models.TextField()
    position = models.TextField()
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    clinic = models.ForeignKey('clinicApp.Organization', on_delete=models.CASCADE, db_column='ext_id', related_name='doctors')
    working_days = models.CharField(max_length=28, choices=DAYS_OF_WEEK, default="Пон, Вто, Сре, Чет, Пят, Суб, Вос")
    profile_pic = models.ImageField(upload_to='doctor_images/', null=True, blank=True)

    def is_working_day(self, day):
        return day in self.working_days.split(', ')


    def __str__(self):
        return f"{self.full_name} - {self.position}"










from django.db import models

class Attachment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, to_field='iin', related_name='attachments', db_column='patient_iin')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='patient_attachments', db_column='doctor_iin')
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='patient_attachments', db_column='organization_ext_id')
    date_attached = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # Поле, указывающее, активна ли эта запись

    def __str__(self):
        status = "Активное" if self.active else "Историческое"
        return f"{self.patient.first_name} {self.patient.last_name} прикреплен к {self.doctor.full_name} в {self.organization.name} ({status})"




class Appointment(models.Model):
    # Статусы записи
    STATUS_CHOICES = (
        ('scheduled', 'Активно'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, to_field='iin', related_name='appointments')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, to_field='iin', related_name='appointments')
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, db_column='organization_ext_id', related_name='appointments')
    date_time = models.DateTimeField() # Дата и время приема
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Appointment for {self.patient} with {self.doctor} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        # Опционально: добавьте дополнительные настройки, такие как уникальные вместе или порядок по умолчанию
        ordering = ['-date_time']

class Slide(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='slides_images/')

    def __str__(self):
        return self.title