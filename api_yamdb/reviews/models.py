from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
