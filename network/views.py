from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Product
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'model']
    ordering_fields = ['name', 'release_date']


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели NetworkNode
    """
    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country']  # Фильтрация по стране
    search_fields = ['name', 'city', 'country']
    ordering_fields = ['name', 'city', 'created_at', 'debt']

    def get_queryset(self):
        """
        Оптимизация запросов: подгружаем связанные данные
        """
        return NetworkNode.objects.all().select_related('supplier').prefetch_related('products')
