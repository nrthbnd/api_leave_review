from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (
    CategoryViewSet, GenreViewSet, TitleViewSet, CommentViewSet, ReviewViewSet,
    ConfirmationView, token
)

app_name = 'api'

router = SimpleRouter()

router.register('v1/titles', TitleViewSet)
router.register('v1/genres', GenreViewSet)
router.register('v1/categories', CategoryViewSet)
router.register(
    r'v1/titles/(?P<titles_id>\d+)/reviews',
    CommentViewSet,
    basename='reviews',
)
router.register(
    r'titles/(?P<titles_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
    ReviewViewSet,
    basename='reviews',
)

urlpatterns = [
    path('', include(router.urls)),
    path('v1/auth/signup/', ConfirmationView.as_view(), name='signup'),
    path('v1/auth/token/', token, name='login'),
]
