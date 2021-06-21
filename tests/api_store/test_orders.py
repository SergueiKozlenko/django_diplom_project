import pytest
from django.urls import reverse
import decimal
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, \
    HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_order_create(api_client, product_factory, user_factory):
    """Тест на создание заказа авторизованным пользователем и
     невозможность создания неавторизованным пользователем"""

    products = product_factory(_quantity=2)
    payload = {
        "products": [
            {"product": products[0].id, "quantity": 2},
            {"product": products[1].id, "quantity": 4}
        ]
    }
    expected_ids_set = [(position["product"], position["quantity"]) for position in payload['products']]
    expected_total_amount = products[0].price * 2 + products[1].price * 4
    test_user = user_factory()
    url = reverse('orders-list')

    resp_not_authenticated = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=test_user)
    resp_authenticated = api_client.post(url, payload, format='json')
    result_ids_set = [(position["id"], position["quantity"]) for position in resp_authenticated.json()['products']]
    result_total_amount = decimal.Decimal(resp_authenticated.json()['total_amount'])

    assert resp_not_authenticated.status_code == HTTP_401_UNAUTHORIZED
    assert resp_authenticated.status_code == HTTP_201_CREATED
    assert result_ids_set == expected_ids_set
    assert result_total_amount == expected_total_amount


@pytest.mark.django_db
def test_order_detail(api_client, product_factory, order_factory, user_factory):
    """Тест на получение одного конкретного курса:
    - неавторизованный пользователь - отказ в просмотре.
    - пользователь видит только свой заказ,
    - админ видит все заказы."""

    order = order_factory()
    test_user_owner = order.user
    test_user_not_owner = user_factory()
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    url = reverse('orders-detail', args=[order.id])

    resp_not_authenticated = api_client.get(url)
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.get(url)
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.get(url)
    api_client.force_authenticate(user=test_user_admin)
    resp_admin = api_client.get(url)

    assert resp_not_authenticated.status_code == HTTP_401_UNAUTHORIZED
    assert resp_owner.status_code == HTTP_200_OK
    assert resp_owner.json()['id'] == order.id
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN
    assert resp_admin.status_code == HTTP_200_OK
    assert resp_admin.json()['id'] == order.id


@pytest.mark.django_db
def test_order_list(api_client, order_factory, user_factory):
    """Тест на получение списка заказов (list-логика):
    - неавторизованный пользователь - отказ в просмотре,
    - пользователь видит только свои заказы,
    - админ видит все заказы."""

    orders = order_factory(_quantity=10)
    random_order = random.choice(orders)
    test_user = random_order.user
    test_user_expected_ids_set = {order.id for order in orders if test_user.id == order.user.id}
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    admin_expected_ids_set = {order.id for order in orders}
    url = reverse('orders-list')

    resp_not_authenticated = api_client.get(url)
    api_client.force_authenticate(user=test_user)
    resp_test_user = api_client.get(url)
    result_test_user_ids_set = {order['id'] for order in resp_test_user.json()}
    api_client.force_authenticate(user=test_user_admin)
    resp_admin = api_client.get(url)
    result_admin_ids_set = {order['id'] for order in resp_admin.json()}

    assert resp_not_authenticated.status_code == HTTP_401_UNAUTHORIZED
    assert resp_test_user.status_code == HTTP_200_OK
    assert result_test_user_ids_set == test_user_expected_ids_set
    assert resp_admin.status_code == HTTP_200_OK
    assert result_admin_ids_set == admin_expected_ids_set


@pytest.mark.django_db
def test_order_update(api_client, product_factory, order_factory, user_factory):
    """Тест на изменение позиций заказа:
    - неавторизованный пользователь - отказ,
    - пользователь может менять только свой заказ,
    - админ может менять все заказы."""

    order = order_factory()
    new_product = product_factory()
    payload = {
        "products": [
            {
                "product": new_product.id,
                "quantity": 5
            }
        ]
    }
    test_user_owner = order.user
    test_user_not_owner = user_factory()
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    url = reverse('orders-detail', args=[order.id])

    resp_not_authenticated = api_client.put(url, payload, format='json')
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.put(url, payload, format='json')
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.put(url, payload, format='json')
    api_client.force_authenticate(user=test_user_admin)
    resp_admin = api_client.put(url, payload, format='json')

    assert resp_not_authenticated.status_code == HTTP_401_UNAUTHORIZED
    assert resp_owner.status_code == HTTP_200_OK
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN
    assert resp_admin.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_order_update_status(api_client, order_factory, user_factory):
    """Тест на изменение статуса заказа:
    - неавторизованный пользователь - отказ,
    - пользователь - отказ,
    - админ может менять статус любого заказа."""

    order = order_factory()
    payload = {
        "status": "DONE"
    }
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    test_user_owner = order.user
    api_client.force_authenticate(user=test_user_owner)
    url = reverse('orders-detail', args=(order.id,))

    resp_owner = api_client.patch(url, payload, format='json')
    api_client.force_authenticate(user=test_user_admin)
    resp_admin = api_client.patch(url, payload, format='json')
    resp_admin_json = resp_admin.json()

    assert resp_owner.status_code == HTTP_400_BAD_REQUEST
    assert resp_admin.status_code == HTTP_200_OK and resp_admin_json['status'] == 'DONE'


@pytest.mark.django_db
def test_order_filter_status(api_client, order_factory, user_factory):
    """
    Тест фильтра по статусу заказа.
    """
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    order_factory(_quantity=5, status='NEW')
    order_factory(_quantity=4, status='IN_PROGRESS')
    done_orders = order_factory(_quantity=3, status='DONE')
    done_expected_ids_set = {order.id for order in done_orders}
    url = reverse('orders-list')

    api_client.force_authenticate(user=test_user_admin)
    resp_done = api_client.get(url, {'status': 'DONE'})
    results = resp_done.json()
    result_done_ids_set = {order['id'] for order in results}

    assert resp_done.status_code == HTTP_200_OK
    assert result_done_ids_set == done_expected_ids_set


@pytest.mark.django_db
def test_order_filter_total(api_client, order_factory, user_factory):
    """
    Тест фильтра по общей сумме заказа.
    """
    orders = []
    for number in range(1, 10):
        orders.append(order_factory(total_amount=random.randrange(100, 10000)))
    filter_value = sorted([order.total_amount for order in orders])[4]
    expected_set_from = {(order.id, order.total_amount) for order in orders if order.total_amount >= filter_value}
    expected_set_to = {(order.id, order.total_amount) for order in orders if order.total_amount <= filter_value}
    test_user_admin = user_factory()
    test_user_admin.is_staff = True
    api_client.force_authenticate(user=test_user_admin)
    url = reverse('orders-list')

    resp_from = api_client.get(url, {'total_amount_from': filter_value})
    result_set_from = {(order['id'], decimal.Decimal(order['total_amount'])) for order in resp_from.json()}
    resp_to = api_client.get(url, {'total_amount_to': filter_value})
    result_set_to = {(order['id'], decimal.Decimal(order['total_amount'])) for order in resp_to.json()}

    assert resp_from.status_code == HTTP_200_OK
    assert result_set_from == expected_set_from
    assert resp_to.status_code == HTTP_200_OK
    assert result_set_to == expected_set_to
