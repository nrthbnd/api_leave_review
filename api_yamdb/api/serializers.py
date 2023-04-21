from rest_framework import serializers
from django.core.exceptions import ValidationError

from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment


class EmailSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()


class GenreSerializer(serializers.ModelSerializer):
    # titles = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    # category = serializers.StringRelatedField(read_only=True)
    genre = GenreSerializer(many=True, required=False)
    description = serializers.StringRelatedField(required=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def create(self, validated_data):
        if 'genre' not in self.initial_data:
            name = Title.objects.create(**validated_data)
            return name
        genres = validated_data.pop('genre')
        name = Title.objects.create(**validated_data)
        for genre in genres:
            current_genre, status = Genre.objects.get_or_create(**genre)
            GenreTitle.objects.create(genre=current_genre, name=name)
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
        if 0 < value < 11:
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
