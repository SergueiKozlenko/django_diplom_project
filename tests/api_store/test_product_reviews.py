import pytest
from django.urls import reverse
import random
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, \
    HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_review_create(api_client, product_factory, user_factory):
    """Тест на невозможность создания отзыва неавторизованным пользователем,
    на создание отзыва авторизованным пользователем,
    невозможность создания второго отзыва на один и то же товар."""

    product_for_review = product_factory()
    payload = {
        'product_id': product_for_review.id,
        'text': 'test review text',
        'rating': 3
    }
    url = reverse('product-reviews-list')
    test_user = user_factory()

    resp_not_authenticated = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=test_user)
    resp_authenticated = api_client.post(url, payload, format='json')
    resp_authenticated_2 = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)

    assert resp_not_authenticated.status_code == HTTP_401_UNAUTHORIZED
    assert resp_authenticated.status_code == HTTP_201_CREATED
    assert resp_authenticated_2.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_product_review_detail(api_client, product_review_factory):
    """
    Тест на вывод одного конкретного отзыва.
    """
    review = product_review_factory()
    url = reverse('product-reviews-detail', args=(review.id,))

    resp = api_client.get(url)
    result = resp.json()

    assert resp.status_code == HTTP_200_OK
    assert result['id'] == review.id


@pytest.mark.django_db
def test_product_review_list(api_client, product_review_factory):
    """
    Тест на вывод списка отзывов.
    """
    reviews = product_review_factory(_quantity=7)
    expected_ids_set = {review.id for review in reviews}
    url = reverse('product-reviews-list')

    resp = api_client.get(url)
    result_ids_set = {review['id'] for review in resp.json()}

    assert resp.status_code == HTTP_200_OK
    assert result_ids_set == expected_ids_set


@pytest.mark.django_db
def test_product_review_update(api_client, product_review_factory, user_factory):
    """Тест на изменение/удаление отзыва автором и
     невозможность изменения/удаления другим пользователем."""

    review = product_review_factory()
    id_for_update = review.id
    url = reverse('product-reviews-detail', args=(id_for_update,))
    payload = {
        'product_id': review.product.id,
        'text': 'test review text',
        'rating': 3
    }
    test_user_owner = review.user
    test_user_not_owner = user_factory()

    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.put(url, payload, format='json')
    destroy_not_owner = api_client.delete(url, format='json')
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.put(url, payload, format='json')
    destroy_owner = api_client.delete(url, format='json')

    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN
    assert destroy_not_owner.status_code == HTTP_403_FORBIDDEN
    assert resp_owner.status_code == HTTP_200_OK
    assert destroy_owner.status_code == HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_review_filter_user(api_client, product_review_factory):
    """
    Тест фильтра списка отзывов по id пользователя.
    """
    reviews = product_review_factory(_quantity=10)
    random_user = random.choice(reviews).user
    expected_ids_set = {review.id for review in reviews if review.user.id == random_user.id}
    url = reverse('product-reviews-list')

    resp = api_client.get(url, {'user_id': random_user.id})
    result_ids_set = {review['id'] for review in resp.json()}

    assert resp.status_code == HTTP_200_OK
    assert result_ids_set == expected_ids_set


@pytest.mark.django_db
def test_product_review_filter_product(api_client, product_review_factory):
    """
    Тест фильтра списка отзывов по id товара.
    """
    reviews = product_review_factory(_quantity=10)
    random_product = random.choice(reviews).product
    expected_ids_set = {review.id for review in reviews if review.product.id == random_product.id}
    url = reverse('product-reviews-list')

    resp = api_client.get(url, {'product_id': random_product.id})
    result_ids_set = {review['id'] for review in resp.json()}

    assert resp.status_code == HTTP_200_OK
    assert result_ids_set == expected_ids_set
