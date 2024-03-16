from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import Patient

class CustomPatientAdmin(UserAdmin):
    model = Patient
    list_display = ('iin', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('iin', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('iin', 'email')}),
        ('Change password', {'fields': ('change_password',)}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('iin', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

    ordering = ('id',)
    readonly_fields = ('last_login', 'change_password',)

    def change_password(self, obj):
        if obj.pk:  # Проверяем, что объект уже сохранен (у него есть первичный ключ)
            return format_html(
                '<a class="button" href="{}">Change password</a>',
                reverse('admin:auth_user_password_change', args=[obj.pk])
            )
        return "You can change the password after saving."

    # Мы переопределяем данный метод для изменения отображения поля password
    def get_fieldsets(self, request, obj=None):
        if not obj:  # Если создается новый объект
            return self.add_fieldsets
        return super(CustomPatientAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomPatientAdmin, self).get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser',
                'user_permissions',
            }

        # Prevent non-superusers from editing their own permissions
        if (
            not is_superuser
            and obj is not None
            and obj == request.user
        ):
            disabled_fields |= {
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    change_password.short_description = "Password"
    change_password.allow_tags = True

# Регистрируем модель и класс администратора
admin.site.register(Patient, CustomPatientAdmin)


