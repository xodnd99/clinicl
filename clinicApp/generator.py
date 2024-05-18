import random
from django.core.files.base import ContentFile
from clinicApp.models import Doctor, Organization
import base64
import time

# Русские имена, фамилии и отчества
russian_names = {
    'male': {
        'first_names': ["Иван", "Петр", "Сергей", "Алексей", "Дмитрий"],
        'last_names': ["Иванов", "Петров", "Сидоров", "Алексеев", "Дмитриев"],
        'patronymics': ["Иванович", "Петрович", "Сергеевич", "Алексеевич", "Дмитриевич"]
    },
    'female': {
        'first_names': ["Мария", "Анна", "Екатерина", "Елена", "Наталья"],
        'last_names': ["Иванова", "Петрова", "Сидорова", "Алексеева", "Дмитриева"],
        'patronymics': ["Ивановна", "Петровна", "Сергеевна", "Алексеевна", "Дмитриевна"]
    }
}

# Казахские имена и фамилии (отчества в казахской культуре не используются так же широко)
kazakh_names = {
    'male': {
        'first_names': ["Асан", "Болат", "Даулет", "Ерлан", "Жасулан"],
        'last_names': ["Муратов", "Жумагулов", "Токтаров", "Ермеков", "Нургалиев"]
    },
    'female': {
        'first_names': ["Карлыгаш", "Малика", "Айман", "Гульназ", "Алия"],
        'last_names': ["Муратова", "Жумагулова", "Токтарова", "Ермекова", "Нургалиева"]
    }
}

DAYS_OF_WEEK = [
    'Пон', 'Вто', 'Сре', 'Чет', 'Пят'
]


def random_working_days():
    # Генерация от 2 до 4 случайных рабочих дней
    return ','.join(random.sample(DAYS_OF_WEEK, random.randint(3, 5)))


# Функция для генерации случайного ИИН
def generate_iin():
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])


# Функция для генерации случайного номера телефона
def generate_phone_number():
    return f"+7{random.randint(1000000000, 9999999999)}"


# Должности врачей
positions = ["Врач общей практики", "Педиатр", "Терапевт"]


def transliterate(name):
    letters = {
        'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
        'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e',
        'Ё': 'E', 'ё': 'e', 'Ж': 'Zh', 'ж': 'zh', 'З': 'Z', 'з': 'z',
        'И': 'I', 'и': 'i', 'Й': 'Y', 'й': 'y', 'К': 'K', 'к': 'k',
        'Л': 'L', 'л': 'l', 'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n',
        'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
        'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u',
        'Ф': 'F', 'ф': 'f', 'Х': 'Kh', 'х': 'kh', 'Ц': 'Ts', 'ц': 'ts',
        'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shch', 'щ': 'shch',
        'Ъ': '', 'ъ': '', 'Ы': 'Y', 'ы': 'y', 'Ь': '', 'ь': '',
        'Э': 'E', 'э': 'e', 'Ю': 'Yu', 'ю': 'yu', 'Я': 'Ya', 'я': 'ya',
        'Ғ': 'G', 'ғ': 'g', 'Қ': 'Q', 'қ': 'q', 'Ң': 'Ng', 'ң': 'ng',
        'Ө': 'O', 'ө': 'o', 'Ұ': 'U', 'ұ': 'u', 'Ү': 'U', 'ү': 'u',
        'Һ': 'H', 'һ': 'h'
    }
    transliterated = ''.join(letters.get(char, char) for char in name)
    return transliterated


def generate_email(last_name, first_name):
    transliterated_last_name = transliterate(last_name)
    transliterated_first_name = transliterate(first_name[0])
    base_email = f"{transliterated_last_name.lower()}.{transliterated_first_name.lower()}@clinics.kz"

    email = base_email
    counter = 1
    while Doctor.objects.filter(email=email).exists():
        if counter <= len(first_name):
            transliterated_first_name_extended = transliterate(first_name[:counter + 1])
            email = f"{transliterated_last_name.lower()}.{transliterated_first_name_extended.lower()}@clinics.kz"
        else:
            email = f"{transliterated_last_name.lower()}.{transliterated_first_name.lower()}{counter}@clinics.kz"
        counter += 1

    return email


def generate_full_name_and_email(nationality, gender):
    if nationality == 'kazakh':
        names_pool = kazakh_names
    else:
        names_pool = russian_names

    first_name = random.choice(names_pool[gender]['first_names'])
    last_name = random.choice(names_pool[gender]['last_names'])
    if nationality == 'russian':
        patronymic = random.choice(names_pool[gender]['patronymics'])
        full_name = f"{last_name} {first_name} {patronymic}"
    else:
        full_name = f"{last_name} {first_name}"

    email = generate_email(last_name, first_name)

    return full_name, email


organizations = Organization.objects.all()
for org in organizations:
    print(f"Processing organization: {org.name}")
    for _ in range(6):  # Предположим, мы хотим добавить по 6 врачей для каждой организации
        nationality = random.choice(['russian', 'kazakh'])
        gender = random.choice(['male', 'female'])
        full_name, email = generate_full_name_and_email(nationality, gender)
        working_days = random_working_days()

        doctor = Doctor(
            iin=generate_iin(),
            full_name=full_name,
            position=random.choice(positions),
            email=email,
            phone_number=generate_phone_number(),
            clinic=org,
            working_days=working_days
        )
        doctor.set_password('defaultpassword')  # Устанавливаем хэшированный пароль
        doctor.save()
        print(f"Created doctor: {doctor.full_name}, email: {doctor.email}, clinic: {org.name}")
