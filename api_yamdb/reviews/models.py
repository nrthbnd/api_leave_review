from django.db import models
from django.contrib.auth.models import AbstractUser


SCORE_LIMIT = [(i, i) for i in range(1, 11)]


class User(AbstractUser):
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'
    ROLES = [
        (USER, 'Аутентифицированный пользователь'),
        (MODER, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        # validators=[validate_username]
        )
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    email = models.EmailField('Почта', unique=True, max_length=254)
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField(
        'Роль',
        max_length=250,
        choices=ROLES,
        default=USER
    )
    confirmation_code = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Код для идентификации'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_together'
            )
        ]


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(
        verbose_name='Год создания',
    )
    rating = models.IntegerField(default=0)
    description = models.TextField(
        'Описание',
        help_text='Описанdие произведения',
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
        verbose_name_plural = 'Название произведении'
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
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Название произведения',
        help_text='Название произведения',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор',
        help_text='Что то про автора',
    )
    score = models.IntegerField(choices=SCORE_LIMIT)
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
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='Название произведения',
        help_text='Название произведения',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор',
        help_text='Что то про автора',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'
