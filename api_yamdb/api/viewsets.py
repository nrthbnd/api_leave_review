from rest_framework import mixins, viewsets
from rest_framework.exceptions import MethodNotAllowed


class ListCreateDestroyViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class ListCreateUpdateDestroyViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin,
    mixins.CreateModelMixin, mixins.UpdateModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    """Запрещает метод PUT."""
    def update(self, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Use PATCH")

    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)
