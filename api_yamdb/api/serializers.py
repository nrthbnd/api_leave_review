from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from reviews.validators import validate_username
from reviews.models import (Category, Genre, Title,
                            Review, Comment, User)


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена"""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    confirmation_code = serializers.CharField(
        required=True,
    )


class ConfirmationSerializer(serializers.Serializer):
    """Сериализатор для получения confirmation_code"""
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[validate_username],
    )
    email = serializers.EmailField(
        required=True,
        max_length=254
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
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
    """Сериализатор для категорий"""
    name = serializers.CharField(max_length=256, required=True)
    slug = serializers.SlugField(
        max_length=50,
        validators=[
            RegexValidator(regex=r'^[-a-zA-Z0-9_]+$'),
            UniqueValidator(queryset=Category.objects.all())
        ],
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    name = serializers.CharField(max_length=256, required=True)
    slug = serializers.SlugField(
        max_length=50,
        validators=[
            RegexValidator(regex=r'^[-a-zA-Z0-9_]+$'),
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
    """Сериализатор для SAFE_METHODS к произведениям"""
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
     информации о произведении"""
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

    def validate_review(self, data):
        """Проверка на однократное создание отзыва"""
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
    """Сериализатор для комментариев"""
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


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('__all__')
        model = Review

    def validate(self, data):
        title = self.context.get('view').kwargs.get('title_id')
        author = self.context.get('request').user
        if (
            self.context.get('request').method == 'POST'
            and Review.objects.filter(author=author, title=title).exists()
        ):
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение!'
            )
        return data
