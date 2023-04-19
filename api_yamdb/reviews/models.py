from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(
        verbose_name='Год создания',
        validators=[validate_year],
    )
    rating = 1
    description = models.TextField(
        'Описание',
        help_text='Описание произведения',
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        'Category',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Категория произведения, например: фильм, песня',
        help_text='Категория, к которой будет относиться произведение',
        related_name='titles',
    )

    class Meta:
        verbose_name = 'Название произведения'
        ordering = ['-year']

    def __str__(self) -> str:
        return self.name


class GenreTitle(models.Model):
    """В этой модели связываются название произведения и его жанр"""
    genre_id = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр произведения',
    )
    title_id = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Название произведения',
    )

    def __str__(self):
        return f'{self.title_id} {self.genre_id}'


class Review(models.Model):
    text = models.TextField(
        verbose_name='Текст отзыва',
        help_text='Текст нового отзывы',
    )
    title = 1  # после написания модели Title
    author = 'Вася'  # после написания модели User
    score_limit = [(i, i) for i in range(1, 11)]
    score = models.IntegerField(choices=score_limit)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст нового комментария',
    )
    title = 1  # после написания модели Title
    author = 'Вася'  # после написания модели User
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'
