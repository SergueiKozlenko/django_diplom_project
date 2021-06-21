import decimal
import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT
import random
from django.contrib.auth.models import User
from api_store.models import Product


@pytest.mark.django_db
def test_product_detail(api_client, product_factory):
    """
    Тест получения одного конкретного продукта.
    """
    product = product_factory()
    url = reverse('products-detail', args=[product.id])

    resp = api_client.get(url)

    assert resp.status_code == HTTP_200_OK
    assert resp.json()['id'] == product.id


@pytest.mark.django_db
def test_product_list(api_client, product_factory):
    """
    Тест на вывод списка продуктов.
    """
    products = product_factory(_quantity=10)
    expected_ids_set = {product.id for product in products}
    url = reverse('products-list')

    resp = api_client.get(url)
    result = resp.json()
    result_ids_set = {product['id'] for product in result}

    assert resp.status_code == HTTP_200_OK
    assert expected_ids_set == result_ids_set


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_201_CREATED),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_create(api_client, user_kwargs, expected_status, user_factory):
    """
    Тест на создание продукта администратором и невозможность создания пользователем.
    """
    payload = {
        'name': 'test product',
        'description': 'product description',
        'price': '10000.00'
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('products-list')

    resp = api_client.post(url, payload, format='json')

    assert resp.status_code == expected_status


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_update(api_client, product_factory, user_kwargs, expected_status):
    """
    Тест на изменение продукта администратором и невозможность изменения пользователем.
    """
    products = product_factory(_quantity=7)
    id_for_update = random.choice(products).id
    payload = {
        'name': 'product name update',
        'description': 'product description update',
        'price': 7000.00
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('products-detail', args=(id_for_update,))

    resp = api_client.put(url, payload, format='json')

    assert resp.status_code == expected_status
    if resp.status_code == 200:
        updated_product = Product.objects.get(id=id_for_update)
        assert updated_product.name == payload['name']
        assert updated_product.description == payload['description']
        assert updated_product.price == payload['price']


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_204_NO_CONTENT),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_delete(api_client, product_factory, user_kwargs, expected_status):
    """
    Тест на удаление продукта администратором и невозможность удаления пользователем.
    """
    products = product_factory(_quantity=7)
    id_for_delete = random.choice(products).id
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    url = reverse('products-detail', args=(id_for_delete,))

    resp = api_client.delete(url, format='json')

    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_product_filter_name(api_client, product_factory):
    """
    Тест фильтра списка продуктов по имени.
    """
    products = product_factory(_quantity=7)
    filter_name = random.choice(products).name
    url = reverse('products-list')

    resp = api_client.get(url, {'name': filter_name})
    result = resp.json()
    result_names_set = [product['name'] for product in result]

    assert resp.status_code == HTTP_200_OK
    assert all(str(filter_name) == str(name) for name in result_names_set)


@pytest.mark.django_db
def test_product_filter_description(api_client, product_factory):
    """
    Тест фильтра списка продуктов по описанию.
    """
    products = product_factory(_quantity=7)
    filter_description = random.choice(products).description
    url = reverse('products-list')

    resp = api_client.get(url, {'description': filter_description})
    result_descriptions_set = [product['description'] for product in resp.json()]

    assert resp.status_code == HTTP_200_OK
    assert all(str(filter_description) == str(description) for description in result_descriptions_set)


@pytest.mark.django_db
def test_product_filter_price(api_client, product_factory):
    """
    Тест фильтра списка продуктов по цене.
    """
    products = []
    for number in range(1, 10):
        products.append(product_factory(price=random.randrange(100, 10000)))
    filter_value = sorted([product.price for product in products])[4]
    expected_set_min_price = {(product.id, product.price) for product in products if product.price >= filter_value}
    expected_set_max_price = {(product.id, product.price) for product in products if product.price <= filter_value}
    url = reverse('products-list')

    resp_min = api_client.get(url, {'min_price': filter_value})
    result_set_min_price = {(product['id'], decimal.Decimal(product['price'])) for product in resp_min.json()}
    resp_max = api_client.get(url, {'max_price': filter_value})
    result_set_max_price = {(product['id'], decimal.Decimal(product['price'])) for product in resp_max.json()}

    assert resp_min.status_code == HTTP_200_OK
    assert result_set_min_price == expected_set_min_price
    assert resp_max.status_code == HTTP_200_OK
    assert result_set_max_price == expected_set_max_price
