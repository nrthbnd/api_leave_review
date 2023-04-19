from rest_framework import serializers

from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment


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


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment