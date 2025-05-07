# Проект API для Yamdb

Позволяет делать GET, POST, PUT, PATCH и DELTE запросы к социальной сети YaTube. Также настроены аутентификация и админ-зона для работы администратора.

## Запуск проекта: 

### 1) Клонируем репозиторий:

https://github.com/ilyushkinss/api_yamdb

### 2) Создаем и активируем виртуальное окружение:

python -m venv venv

source venv/Scripts/activate

### 3) Устанавливаем зависимости из requirements:

pip install -r requirements.txt

### 4) Применяем миграции:

python manage.py migrate

### 5) Запускаем проект:

python manage.py runserver