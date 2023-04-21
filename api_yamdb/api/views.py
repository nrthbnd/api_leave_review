from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail

from reviews.models import Category, Genre, Title, Comment, Review
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    CommentSerializer, ReviewSerializer, EmailSerializer)


class EmailView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        send_mail(
            'Subject here',
            'Here is the message.',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        return Response({"email": email, "username": username})


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
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
