from django_filters import rest_framework as filters
from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Определяет фильтры для модели Title:
    name по строке без учета регистра, year в диапазоне дат,
    genre и category через поле slug"""
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    year = filters.RangeFilter()
    category = filters.CharFilter(field_name="category__slug")
    genre = filters.CharFilter(field_name='genre__slug')

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
