from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from reviews.models import Category, Genre, Review, Title, User

from .permissions import IsAdmin, IsAuthorOrModeratorOrReadOnly, ReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializer, TokenSerializer)
from .viewsets import ListCreateDestroyViewSet
from .filters import TitleFilter


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
    """Вьюсет для модели Title"""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = None
    permission_classes = (IsAdmin, ReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = TitleFilter
    ordering_fields = ('name',)


class CategoryGenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет для моделей Category и Genre"""
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fileds = ('name',)
    permission_classes = (IsAdmin,)


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Comment"""
    serializer_class = CommentSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    @property
    def review(self):
        """Возвращает из БД объект review"""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Возвращает все коментарии для объекта review"""
        return self.review.comments.all()

    def perform_create(self, serializer):
        """Сохраняет комментарий с автором и отзывом,
        к которому он оставляется"""
        serializer.save(author=self.request.user, review=self.review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review"""
    serializer_class = ReviewSerializer
    pagination_class = None
    permission_classes = (IsAuthorOrModeratorOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    @property
    def title(self):
        """Возвращает из БД объект title"""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Возвращает все отзывы для объекта title"""
        return self.title.reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв с автором и заголовком,
        полученными из запроса и объектом title"""
        serializer.save(author=self.request.user, title=self.title)
