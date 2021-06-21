from django_filters import rest_framework as filters
from api_store.models import Product, Order, OrderStatusChoices, ProductReview


class ProductFilter(filters.FilterSet):
    """
    FilterSet для товаров.
    """
    name = filters.CharFilter(label='Название')
    description = filters.CharFilter(lookup_expr='icontains', label='Описание')
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte', label='Цена от')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte', label='Цена до')

    class Meta:
        model = Product
        fields = ('name', 'description', 'min_price', 'max_price')


class OrderFilter(filters.FilterSet):
    """
    FilterSet для заказов.
    """
    status = filters.ChoiceFilter(choices=OrderStatusChoices.choices, label='Статус заказа')
    total_amount_from = filters.NumberFilter(field_name="total_amount", lookup_expr='gte', label='Сумма заказа от')
    total_amount_to = filters.NumberFilter(field_name="total_amount", lookup_expr='lte', label='Сумма заказа до')
    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Order
        fields = ('status', 'total_amount_from', 'total_amount_to', 'products', 'created_at', 'updated_at')


class ProductReviewFilter(filters.FilterSet):
    """
    FilterSet для отзывов к товару.
    """
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = ProductReview
        fields = ('user_id', 'product_id', 'created_at')
