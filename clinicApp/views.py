import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.http import require_POST
from .models import PatientDetail



def login_signup_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            email = request.POST.get('email')
            iin = request.POST.get('iin')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            image_data = request.POST.get('capturedImage')
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

            user = authenticate(request, username=iin, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вход успешно выполнен!')
            else:
                messages.error(request, 'Неверный ИИН или пароль')
                return redirect(reverse('login-signup') + '?tab=login')

    return render(request, 'registration/login.html', {
        'tab': 'signup' if request.GET.get('tab') == 'signup' else 'login'
    })


# views.py

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
                login(request, patient)
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
                        <p><img src="{image_url}" alt="Image description" width="200"></p> <!-- Вы можете добавить 'width' и 'height' для контроля размера изображения -->
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


from django.shortcuts import render

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
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Organization, Doctor, Patient, Attachment
from django.views.decorators.csrf import csrf_exempt

def attach_page(request):
    if request.method == 'POST':
        patient_iin = request.user.iin
        doctor_iin = request.POST.get('doctor')
        organization_ext_id = request.POST.get('organization')

        doctor = Doctor.objects.get(iin=doctor_iin)
        organization = Organization.objects.get(ext_id=organization_ext_id)

        # Check if an attachment already exists and update or create accordingly
        attachment, _ = Attachment.objects.update_or_create(
            patient_id=patient_iin,
            defaults={'doctor': doctor, 'organization': organization}
        )
        return JsonResponse({'success': True, 'message': 'Вы успешно прикрепилсь к поликлинике!'})

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
        patient_attachment = Attachment.objects.get(patient__iin=patient_iin)
        attached_clinic = patient_attachment.organization
        attached_doctor = patient_attachment.doctor
        working_days = attached_doctor.working_days if attached_doctor else "Вос,Пон,Вто,Сре,Чет,Пят,Суб"  # default working days

        phone_numbers_list = attached_clinic.phone_numbers.split(',') if attached_clinic.phone_numbers else []
        doctor_image_url = request.build_absolute_uri(
            attached_doctor.profile_pic.url) if attached_doctor and attached_doctor.profile_pic else None
    except Attachment.DoesNotExist:
        attached_clinic = None
        attached_doctor = None
        working_days = "Вос,Пон,Вто,Сре,Чет,Пят,Суб"  # default or empty
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
    attachment = get_object_or_404(Attachment, patient__iin=patient_iin)

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


from .models import Appointment



@csrf_exempt
@require_POST
def create_appointment(request):
    # Assuming that you are receiving a JSON payload
    data = json.loads(request.body)
    date_time_str = f"{data.get('date')} {data.get('time')}"

    # Parse the string to a datetime object making sure to include timezone information
    # Adjust 'Europe/Moscow' to your timezone
    tz = pytz.timezone('Europe/Moscow')
    date_time = timezone.make_aware(parse_datetime(date_time_str), tz)

    # Ensure the patient is authenticated and you retrieve their iin from their session or user object
    appointment = Appointment.objects.create(
        patient_id=request.user.iin,  # Assuming the patient is logged in and request.user is the patient
        doctor_id=data.get('doctor_iin'),
        organization_id=data.get('clinic_id'),
        date_time=date_time,
        status='scheduled',
        comments=''  # If you need to handle comments
    )
    appointment.save()

    return JsonResponse({'success': True})