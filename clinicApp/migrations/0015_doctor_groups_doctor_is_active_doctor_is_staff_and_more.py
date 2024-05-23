# Generated by Django 5.0.4 on 2024-05-19 09:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('clinicApp', '0014_remove_doctor_groups_remove_doctor_is_active_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='doctor_groups', related_query_name='doctor', to='auth.group'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='active'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_staff',
            field=models.BooleanField(default=False, verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='password',
            field=models.CharField(default=1, max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='doctor',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='doctor_permissions', related_query_name='doctor', to='auth.permission'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='clinicApp.patient'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='doctor',
            name='iin',
            field=models.CharField(max_length=12, primary_key=True, serialize=False, unique=True, verbose_name='IIN'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='patient_groups', related_query_name='patient', to='auth.group'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='iin',
            field=models.CharField(max_length=12, primary_key=True, serialize=False, unique=True, verbose_name='IIN'),
        ),
        migrations.AlterField(
            model_name='patient',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='patient_permissions', related_query_name='patient', to='auth.permission'),
        ),
    ]