from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import CategoryViewSet, GenreViewSet, TitleViewSet

app_name = 'api'

router = SimpleRouter()
router.register('titles', TitleViewSet)
router.register('genres', GenreViewSet)
router.register('categories', CategoryViewSet)
# router comments, reviews

urlpatterns = [
    path('v1/', include(router.urls)),
]
