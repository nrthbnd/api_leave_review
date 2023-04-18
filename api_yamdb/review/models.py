from django.db import models


class Title(models.Model):
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(
        'Genre',
        blank=True,
        null=True,
        many=True,
        on_delete=models.SET_NULL,
        verbose_name='Жанр произведения',
        help_text='Жанр(ы), к которому будет относиться произведение',
        related_name='titles',
    )
    category = models.ForeignKey(
        'Category',
        blank=False,
        null=False,
        many=False,
        on_delete=models.SET_NULL,
        verbose_name='Категория произведения, например: фильм, песня',
        help_text='Категория, к которой будет относиться произведение',
        related_name='titles',
    )
    # reviews
    # comments

    class Meta:
        verbose_name = 'Название произведения'

    def __str__(self) -> str:
        return self.title


class Genre(models.Model):
    genre_name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.genre_name


class Category(models.Model):
    category_name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.category_name


# class Review
# class Comment
# author = models.ForeignKey(User, on_delete=models.CASCADE,)
