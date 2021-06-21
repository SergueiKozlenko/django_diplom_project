from django.conf.global_settings import AUTH_USER_MODEL
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class OrderStatusChoices(models.TextChoices):
    """
    Модель статуса заказа.
    """
    NEW = "NEW", "Открыт"
    IN_PROGRESS = "IN_PROGRESS", "Выполняется"
    DONE = "DONE", "Выполнен"


class TimestampFields(models.Model):
    """
    Модель абстрактного базового класса, обеспечивающая самообновление полей created_at и updated_at.
     """
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )

    class Meta:
        abstract = True


class Product(TimestampFields):
    """
    Модель товара.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
    )

    def __str__(self):
        return f"{self.name} - Цена {self.price}"

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-updated_at', '-created_at']


class Position(models.Model):
    """
    Модель позиции товаров в заказе,для m2m-связи Product и Order.
    """
    order = models.ForeignKey(
        'Order',
        related_name='positions',
        on_delete=models.CASCADE,
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )

    def __str__(self):
        return f"Заказ ID_{self.order.id} | Товар - {self.product} | Количество - {self.quantity} "

    class Meta:
        verbose_name = 'Позиция'
        verbose_name_plural = 'Позиции'


class Order(TimestampFields):
    """
    Модель заказа.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    status = models.TextField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.NEW,
        verbose_name='Статус заказа',
    )
    products = models.ManyToManyField(
        Product,
        related_name='order',
        through=Position,
        verbose_name='Позиции'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        verbose_name='Сумма заказа'
    )

    def __str__(self):
        return f'ID_{self.id} - {self.user} | total_amount - {self.total_amount}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-updated_at', '-created_at']


class ProductReview(TimestampFields):
    """
    Модель отзыва к товару.
    """
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='reviews',
        verbose_name='Товар',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )

    def __str__(self):
        return f"ID_{self.id} | {self.product} - {self.user}"

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ["user", "product"]
        ordering = ['-updated_at', '-created_at']


class ProductCollection(TimestampFields):
    """
    Модель подборки товаров.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    products = models.ManyToManyField(
        'Product',
        related_name='product_collections',
        verbose_name='Продукты'
    )

    def __str__(self):
        return f'ID_{self.id} - {self.title}'

    class Meta:
        verbose_name = 'Подборка товаров'
        verbose_name_plural = 'Подборки товаров'
        ordering = ['-updated_at', '-created_at']
