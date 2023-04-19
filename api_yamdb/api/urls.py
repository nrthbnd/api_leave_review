from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import CommentViewSet, ReviewViewSet


app_name = 'api'

router = SimpleRouter()
router.register(
    r'v1/titles/(?P<titles_id>\d+)/reviews',
    CommentViewSet,
    basename='reviews',
)
router.register(
    r'v1/titles/(?P<titles_id>\d+)/reviews/(?P<review_id>\d+)/comments/',
    ReviewViewSet,
    basename='reviews',
)

urlpatterns = [
    path('', include(router.urls)),
]
