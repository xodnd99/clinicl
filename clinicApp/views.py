import paginate
import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.http import require_POST
from .models import PatientDetail
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib import messages
from django.core.files.base import ContentFile

def login_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        is_doctor = request.POST.get('is_doctor') == 'true'

        if action == 'register':
            # Registration logic for patients (assuming doctors cannot self-register)
            email = request.POST.get('email')
            iin = request.POST.get('iin')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            image_data = request.POST.get('capturedImage', None)
            photo = None

            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                photo = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

            if not (iin.isdigit() and len(iin) == 12):
                messages.error(request, 'ИИН должен состоять ровно из 12 цифр')
                return redirect(reverse('login-signup') + '?tab=signup')

            if Patient.objects.filter(email=email).exists():
                messages.error(request, 'Этот email уже используется')
            elif Patient.objects.filter(iin=iin).exists():
                messages.error(request, 'Этот ИИН уже используется')
            else:
                user = Patient.objects.create_user(email=email, iin=iin, password=password, first_name=first_name,
                                                   last_name=last_name, photo=photo)
                messages.success(request, 'Регистрация успешна. Пожалуйста, войдите в систему.')
            return redirect(reverse('login-signup') + '?tab=login')

        elif action == 'login':
            iin = request.POST.get('iin')
            password = request.POST.get('password')

            if not (iin.isdigit() and len(iin) == 12):
                messages.error(request, 'ИИН должен состоять ровно из 12 цифр')
                return redirect(reverse('login-signup') + '?tab=login')

            if is_doctor:
                user = authenticate(request, username=iin, password=password, backend='clinicApp.backends.DoctorBackend')
                if user is not None:
                    login(request, user, backend='clinicApp.backends.DoctorBackend')
                    return redirect('doctor-home')
                else:
                    messages.error(request, 'Неверный ИИН или пароль')
                    return redirect(reverse('login-signup') + '?tab=login')
            else:
                user = authenticate(request, username=iin, password=password, backend='clinicApp.backends.PatientBackend')
                if user is not None:
                    login(request, user, backend='clinicApp.backends.PatientBackend')
                    messages.success(request, 'Вход успешно выполнен!')
                    return redirect('home')
                else:
                    messages.error(request, 'Неверный ИИН или пароль')
                    return redirect(reverse('login-signup') + '?tab=login')

    return render(request, 'registration/login.html', {
        'tab': 'signup' if request.GET.get('tab') == 'signup' else 'login'
    })

from django.contrib.auth.decorators import login_required

@login_required
def doctor_home(request):
    return render(request, 'html/doctor-index.html')




from django.http import JsonResponse
from .utils import classify_face  # Ensure this is pointing to the correct utility function
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import base64

@csrf_exempt
def find_user_view(request):
    if request.method == 'POST':
        photo_data = request.POST.get('photo')
        format, imgstr = photo_data.split(';base64,')
        data = ContentFile(base64.b64decode(imgstr), name='temp.png')

        # Assuming you have a utility function that takes an image and returns the patient's iin
        patient_iin = classify_face(data)

        if patient_iin:
            patient = Patient.objects.filter(iin=patient_iin).first()
            if patient:
                login(request, patient, backend='clinicApp.backends.PatientBackend')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Аутентификация не удалась. Пожалуйста, повторите попытку!'}, status=401)
        else:
            return JsonResponse({'error': 'Лицо не распознано. Пожалуйста, войдите другим способом или повторите попытку!'}, status=400)

    return JsonResponse({'error': 'Неверный запрос. Пожалуйста, повторите попытку!'}, status=400)





@login_required
@require_POST
@csrf_exempt
def save_user_info(request):
    try:
        # Загрузите данные из запроса
        data = json.loads(request.body.decode('utf-8'))
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        district = data.get('district')
        address = data.get('address')
        birth_date = data.get('birth_date')


        # Обновление информации о пациенте (который является пользователем)
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Обновление или создание детальной информации о пациенте
        details, created = PatientDetail.objects.get_or_create(patient=user)  # использование user как patient

        details.phone_number = phone_number if phone_number is not None else details.phone_number
        details.address = address if address is not None else details.address
        details.district = district if district is not None else details.district
        if birth_date:
            details.birth_date = parse_date(birth_date)
        else:
            details.birth_date = None

        details.save()

        return JsonResponse({'status': 'success', 'message': 'Информация успешно обновлена.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})




from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.conf import settings
EMAIL_HOST_USER = settings.EMAIL_HOST_USER
User = get_user_model()



@csrf_exempt
def send_reset_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            code = random.randint(10000, 99999)  # Генерация 4-значного кода
            user.reset_code = str(code)
            user.reset_code_created_at = timezone.now()
            user.save()

            subject = f'Привет, {user.first_name} {user.last_name}! Ваш код для сброса пароля'
            html_message = f"""
                <html>
                    <body>
                        <p>Привет, {user.first_name} {user.last_name}! Ваш код для сброса пароля:</p>
                        <p><b>Код:</b> {code}</p>
                        <p><img src="https://miro.medium.com/v2/resize:fit:720/format:webp/1*lplkDh6PsFYUB7bPPo1kPg.gif" alt="Animated Image"></p>
                    </body>
                </html>
            """

            send_mail(
                subject,
                '',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=html_message
            )
            return JsonResponse({'status': 'success', 'message': 'Код отправлен вам на почту'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден'})

    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')

        try:
            user = User.objects.get(email__iexact=email, reset_code=code)
            # Убедитесь, что временная метка существует и код ещё действителен
            if user.reset_code_created_at and timezone.now() <= user.reset_code_created_at + timezone.timedelta(minutes=30):
                user.set_password(new_password)  # Это сохранит хэшированный пароль
                user.reset_code = None
                user.reset_code_created_at = None
                user.save()  # Важно: не забудьте сохранить объект пользователя!
                return JsonResponse({'status': 'success', 'message': 'Пароль успешно сброшен.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Неверный код сброса или истек срок его действия.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Пользователь не найден.'})

    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})


# views.py
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import random


@csrf_exempt
def send_reset_code_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        iin = data.get('iin')
        user = User.objects.filter(iin=iin).first()

        if user:
            code = random.randint(10000, 99999)  # Генерация 5-значного кода
            user.reset_code = str(code)
            user.reset_code_created_at = timezone.now()
            user.save()

            # Отправка кода на email, ассоциированный с ИИН
            subject = 'Ваш код для сброса пароля'

            # Ссылка на изображение
            image_url = 'https://miro.medium.com/v2/resize:fit:720/format:webp/1*lplkDh6PsFYUB7bPPo1kPg.gif'  # Замените на реальный URL изображения

            html_message = f"""
                <html>
                    <body>
                        <p>Привет, {user.first_name} {user.last_name}! Ваш код для сброса пароля:</p>
                        <p><b>Код:</b> {code}</p>
                        <p><img src="{image_url}" alt="Image description" width="400"></p> 
                    </body>
                </html>
            """

            # Текстовая версия сообщения
            text_content = strip_tags(html_message)

            # Создаем экземпляр EmailMultiAlternatives
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.EMAIL_HOST_USER,
                [user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

            # Кодируем email для безопасности
            encoded_email = urlsafe_base64_encode(force_bytes(user.email))

            return JsonResponse({
                'status': 'success',
                'message': f'Код отправлен на вашу почту.',
                'encoded_email': encoded_email
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'Пользователь с таким ИИН не найден.'})

    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})


from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

User = get_user_model()

@csrf_exempt
def reset_password_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        iin = data.get('iin')
        code = data.get('code')
        new_password = data.get('new_password')

        # Пытаемся найти пользователя по ИИН
        try:
            user = User.objects.get(iin=iin)
        except User.DoesNotExist:
            # Если пользователь не найден, отправляем соответствующий ответ
            return JsonResponse({'status': 'error', 'message': 'Пользователь с таким ИИН не найден.'})

        # Проверяем, действителен ли код
        if user.reset_code == code and user.reset_code_created_at and timezone.now() <= user.reset_code_created_at + timezone.timedelta(minutes=30):
            user.set_password(new_password)
            user.reset_code = None
            user.reset_code_created_at = None
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Пароль успешно сброшен.'})
        else:
            # Если код неверный или время его действия истекло
            return JsonResponse({'status': 'error', 'message': 'Неверный код сброса или истек срок его действия.'})

    # Если метод запроса не POST
    return JsonResponse({'status': 'error', 'message': 'Неверный запрос'})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Organization
import json

@csrf_exempt
@require_http_methods(["POST"])
def save_organization(request):
    data = json.loads(request.body)
    name = data.get('name')
    address = data.get('address')  # Добавьте адрес в данные, которые вы отправляете с клиента
    url = data.get('url')
    phone_numbers = data.get('phoneNumbers')
    hours_text = data.get('hoursText')
    ext_id = data.get('ext_id')

    # Обновите или создайте новую запись, если она не существует
    org, created = Organization.objects.update_or_create(
        ext_id=ext_id,
        defaults={
            'name': name,
            'address': address,
            'url': url,
            'phone_numbers': phone_numbers,
            'hours_text': hours_text,
        }
    )

    return JsonResponse({'status': 'success', 'created': created})


from django.shortcuts import render, redirect


def profile_link(request):
    # Передайте нужный контекст, если это необходимо
    return render(request, 'html/profile-link.html')




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def handle_image_upload(request):
    profile_pic = request.FILES.get('profile_pic')
    if profile_pic:
        patient, created = PatientDetail.objects.get_or_create(patient=request.user)
        patient.profile_pic = profile_pic
        patient.save()
        return JsonResponse({
            'status': 'success',
            'profile_pic_url': patient.profile_pic.url
        })
    return JsonResponse({'status': 'error'})







# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import Organization, Doctor, Patient, Attachment
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Если вы используете AJAX запросы для отправки данных
def attach_page(request):
    if request.method == 'POST':
        patient_iin = request.user.iin
        doctor_iin = request.POST.get('doctor')
        organization_ext_id = request.POST.get('organization')

        doctor = Doctor.objects.get(iin=doctor_iin)
        organization = Organization.objects.get(ext_id=organization_ext_id)

        # Отметить текущее активное прикрепление как неактивное
        Attachment.objects.filter(patient__iin=patient_iin, active=True).update(active=False)

        # Создание нового активного прикрепления
        new_attachment = Attachment(
            patient_id=patient_iin,
            doctor=doctor,
            organization=organization,
            active=True
        )
        new_attachment.save()

        return JsonResponse({'success': True, 'message': 'Вы успешно прикрепились к новой поликлинике!'})

    else:
        organizations = Organization.objects.all()
        doctors = Doctor.objects.none()  # Initially no doctors are selected

        selected_clinic_ext_id = request.GET.get('clinic_ext_id')
        if selected_clinic_ext_id:
            doctors = Doctor.objects.filter(clinic__ext_id=selected_clinic_ext_id)

        context = {
            'organizations': organizations,
            'doctors': doctors,
            'selected_clinic_ext_id': selected_clinic_ext_id,
        }
        return render(request, 'html/attach-page.html', context)


@csrf_exempt
def get_doctors_by_clinic(request, clinic_ext_id):
    doctors = list(Doctor.objects.filter(clinic__ext_id=clinic_ext_id).values('iin', 'full_name', 'position'))
    return JsonResponse(doctors, safe=False)

@login_required
def appoint_doctor(request):
    patient_iin = request.user.iin

    try:
        patient_attachment = Attachment.objects.get(patient__iin=patient_iin, active=True)
        attached_clinic = patient_attachment.organization
        attached_doctor = patient_attachment.doctor
        working_days = attached_doctor.working_days   # default working days

        phone_numbers_list = attached_clinic.phone_numbers.split(',') if attached_clinic.phone_numbers else []
        doctor_image_url = request.build_absolute_uri(
            attached_doctor.profile_pic.url) if attached_doctor and attached_doctor.profile_pic else None
    except Attachment.DoesNotExist:
        attached_clinic = None
        attached_doctor = None
        working_days = None  # default or empty
        phone_numbers_list = []
        doctor_image_url = None

    doctors = Doctor.objects.filter(clinic=attached_clinic) if attached_clinic else Doctor.objects.none()

    return render(request, 'html/appointmet-doctor.html', {
        'attached_clinic': attached_clinic,
        'attached_doctor': attached_doctor,
        'working_days': working_days,
        'phone_numbers_list': phone_numbers_list,
        'doctor_image_url': doctor_image_url,
        'doctors': doctors
    })




from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Doctor, Attachment

@require_POST
def update_doctor(request):
    patient_iin = request.user.iin
    doctor_iin = request.POST.get('doctor')

    # Получаем объекты доктора и прикрепления. Используйте get_object_or_404 для обработки отсутствующих записей.
    doctor = get_object_or_404(Doctor, iin=doctor_iin)
    attachment = get_object_or_404(Attachment, patient__iin=patient_iin, active=True)

    attachment.doctor = doctor
    attachment.save()
    doctor_image_url = request.build_absolute_uri(doctor.profile_pic.url) if doctor.profile_pic else ''
    return JsonResponse({
        'success': True,
        'doctor': {
            'full_name': doctor.full_name,
            'position': doctor.position,
            'email': doctor.email,
            'phone_number': doctor.phone_number,
            'image_url': doctor_image_url,
            'working_days': doctor.working_days
        }
    })



from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.utils.dateparse import parse_datetime

@csrf_exempt
@require_POST
def create_appointment(request):
    data = json.loads(request.body)
    patient_iin = request.user.iin  # get the patient's IIN from the logged-in user

    # Check if the patient already has an active (scheduled) appointment
    if Appointment.objects.filter(patient_id=patient_iin, status='scheduled').exists():
        return JsonResponse({
            'success': False,
            'error': 'У вас уже есть активная запись.'
        })

    date_time_str = f"{data.get('date')} {data.get('time')}"
    date_time = parse_datetime(date_time_str)

    # Make sure that the date_time is indeed parsed correctly and make it timezone-aware
    if date_time is None:
        return JsonResponse({'success': False, 'error': 'Invalid date-time format.'})

    # Convert the naive datetime to a timezone-aware datetime using the current timezone set in Django settings
    aware_date_time = timezone.make_aware(date_time, timezone.get_current_timezone())

    # Create the appointment
    appointment = Appointment.objects.create(
        patient_id=patient_iin,
        doctor_id=data.get('doctor_iin'),
        organization_id=data.get('clinic_id'),
        date_time=aware_date_time,
        status='scheduled',
        comments=''
    )

    return JsonResponse({'success': True})



from django.shortcuts import render
from .models import Patient, Appointment, Attachment, Doctor

def medical_history(request):
    patient_iin = request.user.iin
    attachments = Attachment.objects.filter(patient__iin=patient_iin).select_related('doctor', 'organization').order_by('-date_attached')
    appointments = Appointment.objects.filter(patient__iin=patient_iin).select_related('doctor', 'organization').order_by('-date_time')

    return render(request, 'html/medical-history.html', {
        'attachments': attachments,
        'appointments': appointments,
    })


from django.http import JsonResponse
import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

logger = logging.getLogger(__name__)

@require_POST
def cancel_appointment(request, appointment_id):
    try:
        appointment = get_object_or_404(Appointment, id=appointment_id, patient__iin=request.user.iin)
        if appointment.date_time > timezone.now():
            appointment.status = 'cancelled'
            appointment.save()
            logger.info(f"Appointment {appointment_id} cancelled successfully.")
            return JsonResponse({'success': True})
        else:
            logger.warning(f"Attempt to cancel a past appointment {appointment_id}.")
            return JsonResponse({'success': False, 'error': 'Нельзя отменить прошедшую запись.'}, status=400)
    except Exception as e:
        logger.error(f"Error in cancelling appointment {appointment_id}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

from .models import Slide

@login_required
def home(request):
    slides = Slide.objects.all()
    return render(request, 'html/index.html', {'slides': slides})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment


@login_required
def doctor_home(request):
    doctor = request.user  # Assuming the user is already authenticated as a doctor
    clinic = doctor.clinic
    phone_numbers = clinic.phone_numbers.split(", ") if clinic.phone_numbers else []

    # Get the list of patients attached to the doctor
    attachments = doctor.patient_attachments.filter(active=True)
    patients = [attachment.patient for attachment in attachments]
    slides = Slide.objects.all()
    # Get all appointments for the doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date_time')

    context = {
        'clinic': clinic,
        'phone_numbers': phone_numbers,
        'patients': patients,
        'appointments': appointments,
        'slides': slides,
        'doctor': doctor,
        'working_days': doctor.working_days,  # Add this line
    }
    return render(request, 'html/doctor-index.html', context)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Appointment

@csrf_exempt
def save_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        comment = data.get('comment')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.comments = comment
            appointment.status = 'completed'  # Update the status to completed
            appointment.save()
            return JsonResponse({'success': True})
        except Appointment.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Appointment not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Patient, Attachment

@csrf_exempt
def detach_patient(request, iin):
    if request.method == 'POST':
        try:
            patient = Patient.objects.get(iin=iin)
            attachments = Attachment.objects.filter(patient=patient)
            attachments.update(active=False)  # Деактивировать все прикрепления пациента
            return JsonResponse({'success': True})
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пациент не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prescription, Doctor, Patient
import json

@csrf_exempt
def create_prescription(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        patient_iin = request.POST.get('patient_iin')
        pdf_file = request.FILES.get('pdf')
        doctor = request.user  # Assuming the user is already authenticated as a doctor

        try:
            patient = Patient.objects.get(iin=patient_iin)
            prescription = Prescription.objects.create(
                category=category,
                doctor=doctor,
                patient=patient,
                pdf_file=pdf_file
            )
            return JsonResponse({'success': True, 'prescription_id': prescription.id})
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пациент не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prescription


@csrf_exempt
def get_prescriptions(request):
    if request.method == 'GET':
        doctor = request.user  # Assuming the user is already authenticated as a doctor
        page_number = request.GET.get('page', 1)
        prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')
        paginator = Paginator(prescriptions, 10)  # 10 рецептов на страницу
        page_obj = paginator.get_page(page_number)

        prescriptions_data = [
            {
                'id': pres.id,
                'category': pres.category,
                'patient_name': f'{pres.patient.first_name} {pres.patient.last_name}',
                'created_at': pres.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'pdf_url': pres.pdf_file.url if pres.pdf_file else ''
            }
            for pres in page_obj
        ]

        return JsonResponse({
            'success': True,
            'prescriptions': prescriptions_data,
            'page_number': page_obj.number,
            'num_pages': paginator.num_pages
        })
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


def download_prescription_pdf(request, prescription_id):
    try:
        prescription = Prescription.objects.get(id=prescription_id)
        response = FileResponse(prescription.pdf_file.open('rb'), as_attachment=True,
                                filename=f'prescription_{prescription_id}.pdf')
        return response
    except Prescription.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Рецепт не найден'})


# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Appointment, Patient, Doctor
import json

@csrf_exempt
def create_appointment_first(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_iin = data.get('patient_iin')
        date_time = data.get('date_time')

        try:
            patient = get_object_or_404(Patient, iin=patient_iin)
            doctor = request.user  # Assuming the user is already authenticated as a doctor
            organization = doctor.clinic

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                organization=organization,
                date_time=date_time,
                status='scheduled'
            )
            return JsonResponse({'success': True, 'appointment_id': appointment.id})
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пациент не найден'})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

from django.shortcuts import render
from django.http import JsonResponse
from .models import Referral
from .utils import send_referral_email

def create_referral(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        purpose = request.POST.get('purpose')
        details = request.POST.get('details')
        patient_iin = request.POST.get('patient_iin')
        doctor = request.user  # Assuming the logged in user is the doctor

        # Найти пациента по IIN
        patient = Patient.objects.get(iin=patient_iin)

        # Создать и сохранить PDF файл
        pdf_file = request.FILES.get('pdf')

        # Создать запись направления
        referral = Referral.objects.create(
            patient=patient,
            doctor=doctor,
            category=category,
            purpose=purpose,
            details=details,
            pdf_file=pdf_file
        )

        # Отправить email с направлением
        send_referral_email(patient, doctor, referral.pdf_file.path)

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Referral


def get_referrals(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search_query', '')

    doctor = request.user  # Ensure the user is a doctor
    referrals = Referral.objects.filter(doctor=doctor)

    if search_query:
        referrals = referrals.filter(
            patient__iin__icontains(search_query) |
            patient__first_name__icontains(search_query) |
            patient__last_name__icontains(search_query)
        )

    paginator = Paginator(referrals.order_by('-created_at'), 10)  # 10 referrals per page
    referrals_page = paginator.get_page(page)

    referrals_list = [
        {
            'category': referral.get_category_display(),
            'purpose': referral.get_purpose_display(),
            'patient_name': f"{referral.patient.first_name} {referral.patient.last_name}",
            'patient_iin': referral.patient.iin,
            'created_at': referral.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'pdf_url': referral.pdf_file.url if referral.pdf_file else '',
        } for referral in referrals_page
    ]

    data = {
        'referrals': referrals_list,
        'page_number': page,
        'num_pages': paginator.num_pages,
        'success': True,
    }

    return JsonResponse(data)



def doctor_profile_link(request):

    return render(request, 'html/doctor_profile.html')

# clinicApp/views.py

from django.shortcuts import render
from .models import Referral

def referrals(request):
    user = request.user
    if user.is_authenticated:
        patient_referrals = Referral.objects.filter(patient=user)
        return render(request, 'html/referrals.html', {'referrals': patient_referrals})
    else:
        return redirect('login')  # Перенаправление на страницу входа, если пользователь не авторизован

from django.shortcuts import render
from .models import Prescription

def prescriptions_view(request):
    # Предполагаем, что у вас есть механизм аутентификации и идентификации пользователя
    patient = request.user  # Получаем объект пациента из текущего пользователя
    prescriptions = Prescription.objects.filter(patient=patient)

    context = {
        'prescriptions': prescriptions,
    }
    return render(request, 'html/prescriptions.html', context)


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import TestResult, Patient, Doctor


@login_required
@csrf_exempt
def create_test_result(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        details = request.POST.get('details')
        patient_iin = request.POST.get('patient_iin')
        pdf_file = request.FILES.get('pdf_file')

        try:
            patient = Patient.objects.get(iin=patient_iin)
        except Patient.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Пациент не найден'})

        doctor = request.user  # Предполагаем, что request.user уже является объектом Doctor

        test_result = TestResult.objects.create(
            category=category,
            details=details,
            patient=patient,
            pdf_file=pdf_file,
            doctor=doctor
        )

        return JsonResponse({'success': True, 'message': 'Результат анализа успешно создан.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import TestResult

def get_test_results(request):
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search_query', '')

    # Фильтрация результатов тестов
    test_results = TestResult.objects.filter(patient__iin__icontains=search_query).order_by('created_at')

    # Пагинация
    paginator = Paginator(test_results, 10)  # Показывать по 10 результатов на странице

    try:
        test_results = paginator.page(page)
    except PageNotAnInteger:
        test_results = paginator.page(1)
    except EmptyPage:
        test_results = paginator.page(paginator.num_pages)

    data = {
        'success': True,
        'test_results': [
            {
                'category': result.get_category_display(),
                'patient_name': f'{result.patient.first_name} {result.patient.last_name}',
                'patient_iin': result.patient.iin,
                'created_at': result.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'pdf_url': result.pdf_file.url if result.pdf_file else None
            }
            for result in test_results
        ],
        'page_number': test_results.number,
        'num_pages': paginator.num_pages
    }

    return JsonResponse(data)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import TestResult

@login_required
def patient_test_results(request):
    patient = request.user # Assuming `request.user` is a Patient
    test_results = TestResult.objects.filter(patient=patient).order_by('-created_at')
    context = {
        'patient': patient,
        'test_results': test_results,
    }
    return render(request, 'html/patient_test_results.html', context)




