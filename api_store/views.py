from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from api_store.filters import ProductFilter, OrderFilter, ProductReviewFilter
from api_store.models import Product, Order, ProductReview, ProductCollection
from api_store.serializers import ProductSerializer, OrderSerializer, ProductCollectionSerializer, \
    ProductReviewSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from api_store.permissions import IsAdminOrOwner


class ProductsViewSet(ModelViewSet):
    """
    Set для товаров.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        """
        Получение прав для действий с товарами.
        """
        if self.action in ["create", "destroy", "update", "partial_update"]:
            permissions = [IsAuthenticated, IsAdminUser]
        else:
            permissions = []
        return [permission() for permission in permissions]


class OrdersViewSet(ModelViewSet):
    """
    ModelViewSet для заказов.
    """
    queryset = Order.objects.all().prefetch_related('products').select_related('user')
    serializer_class = OrderSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OrderFilter
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            self.queryset = self.queryset.filter(user=request.user)
        return super().list(request, *args, **kwargs)

    def get_permissions(self):
        """Получение прав для действий с заказами.
        retrieve, list, create, update, destroy."""

        if self.action in ['retrieve', 'list', 'update', 'partial_update', 'destroy']:
            permissions = [IsAuthenticated, IsAdminOrOwner]
        elif self.action == 'create':
            permissions = [IsAuthenticated]
        else:
            permissions = []
        return [permission() for permission in permissions]


class ProductReviewsViewSet(ModelViewSet):
    """
    ModelViewSet для отзывов к товару.
    """
    queryset = ProductReview.objects.all().select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductReviewFilter
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAdminOrOwner]
        elif self.action == 'create':
            permissions = [IsAuthenticated]
        else:
            permissions = []
        return [permission() for permission in permissions]


class ProductCollectionsViewSet(ModelViewSet):
    """
    ModelViewSet для отзывов к товару.
    """
    queryset = ProductCollection.objects.all().prefetch_related('products')
    serializer_class = ProductCollectionSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permissions = [IsAdminUser]
        else:
            permissions = []
        return [permission() for permission in permissions]
