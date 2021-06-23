from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api_store.models import Product, Position, ProductCollection, ProductReview, Order


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer для пользователя.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name',)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer для товара.
    """

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price')


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer для отзыва о товаре.
    """
    product = ProductSerializer(
        read_only=True,
    )
    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'product', 'text', 'rating', 'created_at', 'updated_at')

    def validate(self, data):
        """
        Метод для валидации отзывов. Вызывается при создании и обновлении.
        """
        product_id = self.context['request'].data['product_id']
        if not Product.objects.filter(id=product_id):
            raise serializers.ValidationError('Товара с таким ID не существует')
        return data

    def create(self, validated_data):
        """
        Переопределение метода Create при создании отзывов.
        """
        user = self.context["request"].user
        product_id = self.context['request'].data['product_id']
        reviews_count = ProductReview.objects.filter(user=user.id).filter(product=product_id).count()
        if reviews_count >= 1:
            raise ValidationError("Пользователь уже оставил отзыв на этот товар")
        else:
            validated_data['user'] = user
            validated_data['product'] = Product.objects.get(id=product_id)
        return super().create(validated_data)


class PositionSerializer(serializers.ModelSerializer):
    """
    Serializer для позиций товаров в заказе.
    """
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        required=True,
    )
    quantity = serializers.IntegerField(min_value=1, default=1)

    class Meta:
        model = Position
        fields = ('id', 'product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer для заказов.
    """
    products = PositionSerializer(many=True, source='positions')
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'products', 'total_amount', 'created_at', 'updated_at')

    def validate(self, data):
        """
        Метод для валидации заказов.
        """
        if not self.context['request'].user.is_staff and 'status' in data:
            raise serializers.ValidationError('Статус заказа могут менять только администраторы')
        if 'positions' in data:
            product_ids = set()
            for position in data['positions']:
                product_ids.add(position['product'])
            if len(product_ids) != len(data['positions']):
                raise serializers.ValidationError('Продукты не должны повторяться в заказе')
        return data

    def create(self, validated_data):
        """
        Переопределение метода Create при создании заказов.
        """
        validated_data['user'] = self.context['request'].user
        positions = validated_data.pop('positions')
        validated_data['total_amount'] = 0
        for product in positions:
            price = product['product'].price
            validated_data['total_amount'] += price * product['quantity']
        order = super().create(validated_data)
        if positions:
            to_save = []
            for products in positions:
                to_save.append(
                    Position(
                        product=products['product'],
                        quantity=products['quantity'],
                        order_id=order.id
                    )
                )
            Position.objects.bulk_create(to_save)
            return order

    def update(self, instance, validated_data):
        validated_data['user'] = instance.user
        if 'positions' in validated_data:
            positions = validated_data.pop('positions')
            instance.positions.all().delete()
            total = 0
            for product in positions:
                price = product['product'].price
                total += price * product['quantity']
            instance.total = total
            if positions:
                to_save = []
                for products in positions:
                    to_save.append(
                        Position(
                            product=products['product'],
                            quantity=products['quantity'],
                            order_id=instance.id,
                        )
                    )
                Position.objects.bulk_create(to_save)
        if 'status' in validated_data:
            instance.status = validated_data.pop('status')
        instance.save()
        return instance


class ProductCollectionSerializer(serializers.ModelSerializer):
    """
    Serializer для подборок товаров.
    """
    products = ProductSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = ProductCollection
        fields = ('id', 'title', 'text', 'products', 'created_at', 'updated_at')

    def validate(self, data):
        products = self.context['request'].data['products']
        id_list = []
        for product in products:
            if not Product.objects.filter(id=product['product_id']):
                raise serializers.ValidationError(f"Товар с ID {product['product_id']} не существует")
            id_list.append(product.get('product_id'))
        if len(set(id_list)) != len(id_list):
            raise serializers.ValidationError("Товар в одной подборке не может повторяться")
        return data

    def create(self, validated_data):
        product_ids_list = []
        products = self.context['request'].data['products']
        for product in products:
            product_ids_list.append(product['product_id'])
        validated_data['products'] = Product.objects.filter(id__in=product_ids_list)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        product_ids_list = []
        products = self.context['request'].data['products']
        for product in products:
            product_ids_list.append(product['product_id'])
        instance.products.clear()
        instance.products.add(*product_ids_list)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
