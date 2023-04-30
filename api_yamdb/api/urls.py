from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (CategoryViewSet, CommentViewSet,
                       GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet,
                       token, create_code)

app_name = 'api'
router = SimpleRouter()

router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
router.register('users', UserViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment',
)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/signup/', create_code, name='signup'),
    path('v1/auth/token/', token, name='login'),
]
