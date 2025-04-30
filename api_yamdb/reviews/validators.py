import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(
            'Нельзя добавлять произведения, которые еще не вышли.'
        )


def validate_slug(slug):
    if not re.fullmatch(r'^[-a-zA-Z0-9_]+$', slug):
        raise ValidationError(
            'Слаг категории может содержать только цифры, латинские буквы, '
            'символ нижнего подчеркивания и дефис'
        )


def validate_username(username):
    if username == 'me':
        raise ValidationError('Нельзя использовать имя "me"')
    elif not re.fullmatch(r'^[\w.@+-]+\Z', username):
        raise ValidationError(
            'Имя пользователя может содержать только цифры, латинкие буквы, '
            'а так же символы: "-", "+", ".", "@", "_".'
        )