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


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
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
