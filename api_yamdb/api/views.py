from rest_framework import viewsets, mixins, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Comment, Review, User
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    CommentSerializer, ReviewSerializer, ConfirmationSerializer,
    TokenSerializer
)
# from djoser.views import UserViewSet


@api_view(['POST'])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if user.confirmation_code != confirmation_code:
        return Response(
            'Неверный код', status=status.HTTP_400_BAD_REQUEST
        )
    refresh = RefreshToken.for_user(user)
    token_data = {'token': str(refresh.access_token)}
    return Response(token_data, status=status.HTTP_200_OK)


class ConfirmationView(APIView):

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get_or_create(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
        )[0]
        code = default_token_generator.make_token(user)
        user.confirmation_code = code
        user.save()
        send_mail(
            'Код получения токена',
            f'Ваш код: {code}',
            'user@ya.ru',
            [user.email],
            fail_silently=False,
        )
        return Response(
            {"email": user.email, "username": user.username},
            status=status.HTTP_200_OK
        )


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
