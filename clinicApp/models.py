from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password


class PatientManager(BaseUserManager):
    def create_user(self, iin, email, password=None, **extra_fields):
        if not iin:
            raise ValueError('The given IIN must be set')
        email = self.normalize_email(email)
        user = self.model(iin=iin, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
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
    is_doctor = models.BooleanField(default=False)

    objects = PatientManager()

    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(Group, related_name='patient_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='patient_set', blank=True)

    def __str__(self):
        return str(self.iin)


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


class Organization(models.Model):
    ext_id = models.CharField(max_length=255, primary_key=True)
    name = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    url = models.URLField(max_length=1024, blank=True, null=True)
    phone_numbers = models.TextField(blank=True, null=True)
    hours_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class DoctorManager(BaseUserManager):
    def create_user(self, iin, email, password=None, **extra_fields):
        if not iin:
            raise ValueError('The given IIN must be set')
        email = self.normalize_email(email)
        user = self.model(iin=iin, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, iin, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(iin, email, password, **extra_fields)


class Doctor(AbstractBaseUser, PermissionsMixin):
    DAYS_OF_WEEK = (
        ('Пон', 'Monday'),
        ('Вто', 'Tuesday'),
        ('Сре', 'Wednesday'),
        ('Чет', 'Thursday'),
        ('Пят', 'Friday'),
        ('Суб', 'Saturday'),
        ('Вос', 'Sunday'),
    )
    iin = models.CharField(max_length=12, unique=True, primary_key=True)
    full_name = models.TextField()
    position = models.TextField()
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    clinic = models.ForeignKey('clinicApp.Organization', on_delete=models.CASCADE, db_column='ext_id', related_name='doctors')
    working_days = models.CharField(max_length=128, choices=DAYS_OF_WEEK, default="Пон, Вто, Сре, Чет, Пят, Суб, Вос")
    profile_pic = models.ImageField(upload_to='doctor_images/', null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_doctor = models.BooleanField(default=True)

    objects = DoctorManager()

    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(Group, related_name='doctor_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='doctor_set', blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def is_working_day(self, day):
        return day in self.working_days.split(', ')

    def __str__(self):
        return f"{self.full_name} - {self.position}"


class Attachment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, to_field='iin', related_name='attachments', db_column='patient_iin')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='patient_attachments', db_column='doctor_iin')
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, related_name='patient_attachments', db_column='organization_ext_id')
    date_attached = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        status = "Активное" if self.active else "Историческое"
        return f"{self.patient.first_name} {self.patient.last_name} прикреплен к {self.doctor.full_name} в {self.organization.name} ({status})"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Активно'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
    )

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, to_field='iin', related_name='appointments')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, to_field='iin', related_name='appointments')
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE, db_column='organization_ext_id', related_name='appointments')
    date_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Appointment for {self.patient} with {self.doctor} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-date_time']


# models.py
from django.db import models

class Slide(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='slides_images/')
    source = models.URLField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.title

from django.db import models

class Prescription(models.Model):
    category = models.CharField(max_length=100)
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='prescriptions')
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)

    def __str__(self):
        return f"Prescription for {self.patient} by {self.doctor} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

# models.py
from django.db import models

class Referral(models.Model):
    CATEGORY_CHOICES = [
        ('free', 'Бесплатно по ОСМС'),
        ('paid', 'Платно, оплатите на кассе'),
        ('insurance', 'По страховке'),
        ('charity', 'Благотворительная помощь'),
    ]

    PURPOSE_CHOICES = [
        ('analysis', 'Анализы'),
        ('radiology', 'Диагностика (лучевая)'),
        ('ultrasound', 'УЗИ'),
        ('mri', 'МРТ'),
        ('hospital_treatment', 'Лечение в стационарной больнице'),
        ('sanatorium', 'Лечение в санатории'),
        ('specialist_consultation', 'Консультация специалиста'),
        ('physiotherapy', 'Физиотерапия'),
        ('rehabilitation', 'Реабилитация'),
        ('surgery', 'Хирургическое вмешательство'),
        ('cardiology', 'Кардиология'),
        ('neurology', 'Неврология'),
        ('dermatology', 'Дерматология'),
        ('other', 'Другое'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='referrals')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='referrals')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    purpose = models.CharField(max_length=50, choices=PURPOSE_CHOICES)
    details = models.TextField()
    pdf_file = models.FileField(upload_to='referrals/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Referral for {self.patient} by {self.doctor} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


# models.py

from django.db import models

class TestResult(models.Model):
    CATEGORY_CHOICES = [
        ('blood_test', 'Анализ крови'),
        ('urine_test', 'Анализ мочи'),
        ('radiology', 'Диагностика (лучевая)'),
        ('ultrasound', 'УЗИ'),
        ('mri', 'МРТ'),
        ('other', 'Другое'),
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='test_results')
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='test_results')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    details = models.TextField()
    pdf_file = models.FileField(upload_to='test_results/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test Result for {self.patient} by {self.doctor} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
