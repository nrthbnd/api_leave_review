from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.validators import validate_year
from reviews.models import (Category, Genre, Title,
                            GenreTitle, Review, Comment)


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True,
    )
    confirmation_code = serializers.CharField(
        required=True,
    )


class ConfirmationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений"""
    category = CategorySerializer()
    genre = GenreSerializer(many=True, required=False)
    description = serializers.StringRelatedField(required=False)
    year = serializers.IntegerField(validators=[validate_year])
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'rating', 'name', 'year',
                  'description', 'genre', 'category')

    def create(self, validated_data):
        """Сохранение данных в таблице GenreTitle"""
        genre = validated_data.pop('genre')
        name = Title.objects.create(**validated_data)
        for item in genre:
            current_genre, status = Genre.objects.get_or_create(**item)
            GenreTitle.objects.create(item=current_genre, name=name)
        return name


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate_score(value):
        """Проверка рейтинга, выставляемого пользователем"""
        if value < 1 or value > 10:
            raise ValidationError(
                'Рейтинг должен быть от 1 до 10.'
            )
        return value

    # Валидация повторного отзыва на 1 произведение


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
