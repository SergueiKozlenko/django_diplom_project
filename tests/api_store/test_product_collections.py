import pytest
from django.urls import reverse
from django.contrib.auth.models import User
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT

from api_store.models import ProductCollection


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_201_CREATED),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_create(api_client, product_factory, user_kwargs, expected_status):
    """
    Тест на создание подборки администратором и невозможность создания пользователем.
    """
    products = product_factory(_quantity=5)
    product_ids = [product.id for product in products]
    payload = {
        'title': 'test collection',
        'text': 'collection text',
        'products': [{'product_id': product} for product in product_ids]
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('product-collections-list')

    resp = api_client.post(url, payload, format='json')

    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_product_collection_detail(api_client, product_collection_factory):
    """
    Тест на вывод конкретной подборки.
    """
    collections = product_collection_factory(_quantity=7)
    random_collection = random.choice(collections)
    url = reverse('product-collections-detail', args=(random_collection.id,))

    resp = api_client.get(url)
    result = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert result['id'] == random_collection.id


@pytest.mark.django_db
def test_product_collection_list(api_client, product_collection_factory):
    """
    Тест на вывод списка подборок.
    """
    product_collections = product_collection_factory(_quantity=7)
    expected_ids_set = {collection.id for collection in product_collections}
    url = reverse('product-collections-list')

    resp = api_client.get(url)
    result = resp.json()
    result_ids_set = {collection['id'] for collection in result}

    assert resp.status_code == HTTP_200_OK
    assert result_ids_set == expected_ids_set


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_update(api_client, product_collection_factory, product_factory, user_kwargs,
                                   expected_status):
    """
    Тест на изменение подборки администратором и невозможность изменения пользователем.
    """
    collections = product_collection_factory(_quantity=7)
    collection_for_update = random.choice(collections)
    new_products = product_factory(_quantity=3)
    new_products_ids_set = {product.id for product in new_products}
    payload = {
        'title': 'collection name update',
        'text': 'collection update text',
        'products': [{'product_id': product_id} for product_id in new_products_ids_set]
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('product-collections-detail', args=(collection_for_update.id,))

    resp = api_client.put(url, payload, format='json')

    assert resp.status_code == expected_status
    if resp.status_code == 200:
        updated_collection = ProductCollection.objects.get(id=collection_for_update.id)
        result_products_ids_set = {product.id for product in updated_collection.products.all()}
        assert updated_collection.title == payload['title']
        assert updated_collection.text == payload['text']
        assert result_products_ids_set == new_products_ids_set


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_204_NO_CONTENT),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_delete(api_client, product_collection_factory, user_kwargs, expected_status):
    """
    Тест на удаление подборки администратором и невозможность удаления пользователем.
    """
    collections = product_collection_factory(_quantity=7)
    random_collection = random.choice(collections)
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('product-collections-detail', args=(random_collection.id,))

    resp = api_client.delete(url, format='json')

    assert resp.status_code == expected_status
