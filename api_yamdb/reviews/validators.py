import datetime
import re

from django.core.exceptions import ValidationError


def validate_year(value):
    current_year = datetime.date.today().year
    if value < 0 or value > current_year:
        raise ValidationError(
            'Год должен быть меньше или равен текущему, а также больше 0.'
        )
    return value


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': value},
        )
