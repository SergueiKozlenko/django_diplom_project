import pytest
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """
    Фикстура для клиента API.
    """
    return APIClient()


@pytest.fixture
def product_factory():
    """
    Фикстура для фабрики товаров.
    """
    def factory(**kwargs):
        return baker.make('Product', **kwargs)
    return factory


@pytest.fixture
def order_factory():
    """
    Фикстура для фабрики заказов.
    """
    def factory(**kwargs):
        return baker.make('Order', **kwargs)
    return factory


@pytest.fixture
def user_factory():
    """
    Фикстура для фабрики пользователей.
    """
    def factory(**kwargs):
        return baker.make('User', **kwargs)
    return factory


@pytest.fixture
def product_review_factory():
    """
    Фикстура для фабрики отзывов.
    """
    def factory(**kwargs):
        return baker.make('ProductReview', **kwargs)
    return factory


@pytest.fixture
def product_collection_factory():
    """
    Фикстура для фабрики подборок товаров.
    """
    def factory(**kwargs):
        return baker.make('ProductCollection', **kwargs)
    return factory
