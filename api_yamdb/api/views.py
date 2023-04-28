from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from reviews.models import Category, Genre, Review, Title, User
from .permissions import (IsAdmin, IsAuthorOrModeratorOrAdminOrReadOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserSerializer, ConfirmationSerializer,
                          TokenSerializer)
from .viewsets import ListCreateDestroyViewSet
from .filters import TitleFilter


class ConfirmationView(APIView):
    """Отправка confirmation_code на email, введенный при регистрации"""
    permission_classes = [AllowAny, ]

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


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """Отправка токена при получении confirmation_code и username"""
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


# @api_view(['POST, GET, PATCH, DELETE'])
class UserViewSet(viewsets.ModelViewSet):
    """Получение информации о пользователях и ее редактирование"""
    queryset = User.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAdmin,)
    serializer_class = UserSerializer
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        serializer_class=UserSerializer)
    def me(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Получает список всех произведений"""
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleReadSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = TitleFilter
    ordering_fields = ('name',)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от метода"""
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class CategoryGenreViewSet(ListCreateDestroyViewSet):
    """Вьюсет для моделей Category и Genre"""
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fileds = ('name',)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев"""
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    @property
    def review(self):
        """Возвращает из БД объект review"""
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('titles_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('titles_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов"""
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,
                          IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """Возвращает из БД объект title и все отзывы для него"""
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        """Сохраняет отзыв с автором и заголовком,
        полученными из запроса и объектом title"""
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)
