from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.validators import validate_username
from reviews.models import (Category, Genre, Title,
                            Review, Comment, User)

SLUG_REGEX_VALIDATE = r'^[-a-zA-Z0-9_]+$'


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    confirmation_code = serializers.CharField(
        required=True,
    )


class SignupSerializer(serializers.Serializer):
    """Сериализатор для получения confirmation_code."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
    )

    def validate(self, data):
        user_by_username = User.objects.filter(
            username=data['username']
        ).exists()
        user_email = User.objects.filter(email=data['email']).exists()
        if user_email and not user_by_username:
            raise ValidationError('Вы указали некорректный логин')
        if user_by_username and not user_email:
            raise ValidationError('Вы указали некорректную почту')
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            validate_username,
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            ),
        ]


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""
    name = serializers.CharField(max_length=256, required=True)
    slug = serializers.SlugField(
        max_length=50,
        validators=[
            RegexValidator(regex=SLUG_REGEX_VALIDATE),
            UniqueValidator(queryset=Category.objects.all())
        ],
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""
    name = serializers.CharField(max_length=256, required=True)
    slug = serializers.SlugField(
        max_length=50,
        validators=[
            RegexValidator(regex=SLUG_REGEX_VALIDATE),
            UniqueValidator(queryset=Genre.objects.all())
        ],
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')

    def validate_slug(self, slug):
        """Валидация поля slug группы"""
        if Genre.objects.filter(slug=slug).exists():
            raise ValidationError('Такой slug уже существует.')
        return slug


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для SAFE_METHODS к произведениям."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('__all__',)


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и частичного изменения
     информации о произведении."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'rating', 'name', 'year',
                  'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""
    title = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Review

    def validate_score(self, value):
        """Проверка рейтинга, выставляемого пользователем."""
        if value < 1 or value > 10:
            raise ValidationError(
                'Рейтинг должен быть от 1 до 10.'
            )
        return value

    def validate(self, data):
        """Проверка на однократное создание отзыва."""
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError(
                    'На одно произведение нельзя оставить отзыв дважды.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    review = serializers.SlugRelatedField(
        read_only=True,
        slug_field='text',
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        fields = '__all__'
        model = Comment
