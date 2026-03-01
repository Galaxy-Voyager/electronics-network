from rest_framework import serializers
from .models import NetworkNode, Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Product
    """

    class Meta:
        model = Product
        fields = ['id', 'name', 'model', 'release_date']


class NetworkNodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели NetworkNode
    """
    level_display = serializers.SerializerMethodField()
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all(),
        write_only=True,
        required=False
    )
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'level_display', 'email', 'country', 'city',
            'street', 'house_number', 'products', 'product_ids',
            'supplier', 'supplier_name', 'debt', 'created_at'
        ]
        read_only_fields = ['created_at', 'debt']  # Запрещаем обновление долга через API
        extra_kwargs = {
            'supplier': {'required': False, 'allow_null': True}
        }

    def get_level_display(self, obj):
        """
        Возвращает текстовое отображение уровня иерархии
        """
        return obj.get_level_display()

    def create(self, validated_data):
        """
        Создание нового звена с продуктами
        """
        product_ids = validated_data.pop('product_ids', [])
        node = NetworkNode.objects.create(**validated_data)
        node.products.set(product_ids)
        return node

    def update(self, instance, validated_data):
        """
        Обновление звена с продуктами
        """
        product_ids = validated_data.pop('product_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if product_ids is not None:
            instance.products.set(product_ids)

        return instance
