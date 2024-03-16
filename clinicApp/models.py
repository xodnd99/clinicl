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
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=150)
    iin = models.CharField(_('IIN'), max_length=12, unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)

    objects = PatientManager()

    USERNAME_FIELD = 'iin'
    REQUIRED_FIELDS = ['email']

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        # Здесь больше не вызываем self.save(), чтобы избежать ошибки

    def __str__(self):
        return self.iin

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
