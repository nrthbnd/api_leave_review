from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet, ConfirmationView,
                       GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet)

app_name = 'api'
router = SimpleRouter()

router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register(
    r'titles/(?P<titles_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router.register(
    r'titles/(?P<titles_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
    CommentViewSet,
    basename='comment',
)
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', ConfirmationView.as_view()),
]
