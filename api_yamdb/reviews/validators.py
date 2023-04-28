import datetime
import re

from django.core.exceptions import ValidationError

REGEX_USERNAME = re.compile(r'^[\w.@+-]+')


def validate_year(value):
    """Валидация года создания произведения"""
    current_year = datetime.date.today().year
    if value < 0 or value > current_year:
        raise ValidationError(
            'Год должен быть меньше или равен текущему, а также больше 0.'
        )
    return value


def validate_username(name):
    """Валидация имени пользователя"""
    if name == 'me':
        raise ValidationError('В качестве имени нельзя использовать "me".')
    if not REGEX_USERNAME.fullmatch(name):
        raise ValidationError(
            'Для имени доступны буквы A - Z,  a - z и символы _.+-@')
    return name
