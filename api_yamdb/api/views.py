from rest_framework import viewsets, mixins

from reviews.models import Category, Genre, Title
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    CommentSerializer, ReviewSerializer)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class ListCreateDestroy(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    pass


class GenreViewSet(ListCreateDestroy):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    search_fileds = ('name')


class CategoryViewSet(ListCreateDestroy):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fileds = ('name')
    
    
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
