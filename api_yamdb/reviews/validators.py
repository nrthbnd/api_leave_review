import datetime


def validate_year(value):
    current_year = datetime.date.today().year
    if value > current_year or value < 1800:
        raise ValidationError(
            'Год должен быть меньше или равер текущему, но больше 1800.'
        )
