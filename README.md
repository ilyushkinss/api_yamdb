![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

# Проект API для Yamdb

Позволяет делать GET, POST, PUT, PATCH и DELTE запросы к сервису оценок Yamdb. Также настроены аутентификация и админ-зона для работы администратора.

## Запуск проекта: 

### 1) Клонируем репозиторий:

https://github.com/ilyushkinss/api_yamdb

### 2) Создаем и активируем виртуальное окружение:

python3 -m venv venv

source venv/bin/activate

### 3) Устанавливаем зависимости из requirements:

pip install -r requirements.txt

### 4) Применяем миграции:

python manage.py migrate

### 5) Запускаем проект:

python manage.py runserver
