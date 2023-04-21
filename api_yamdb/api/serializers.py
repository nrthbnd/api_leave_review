import datetime
from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment


class EmailSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, required=False)
    description = serializers.StringRelatedField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(value):
        current_year = datetime.date.today().year
        if value > current_year or value < 1800:
            raise ValidationError(
                'Год должен быть меньше или равен текущему, но больше 1800.'
            )

    def create(self, validated_data):
        genre = validated_data.pop('genre')
        name = Title.objects.create(**validated_data)
        for item in genre:
            current_genre, status = Genre.objects.get_or_create(**item)
            GenreTitle.objects.create(item=current_genre, name=name)
        return name


class CategorySerializer(serializers.ModelSerializer):
    titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'titles')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate_score(value):
        if value < 1 or value > 10:
            raise ValidationError(
                'Рейтинг должен быть от 1 до 10.'
            )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
