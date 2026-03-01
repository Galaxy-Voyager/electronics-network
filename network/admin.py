from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import NetworkNode, Product


@admin.action(description="Очистить задолженность перед поставщиком")
def clear_debt(modeladmin, request, queryset):
    """
    Admin action для очистки задолженности у выбранных объектов
    """
    queryset.update(debt=0)


class ProductInline(admin.TabularInline):
    """
    Inline для отображения продуктов на странице звена сети
    """
    model = NetworkNode.products.through
    extra = 1
    verbose_name = "Продукт"
    verbose_name_plural = "Продукты"


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    """
    Настройка админ-панели для модели NetworkNode
    """
    list_display = (
        'name',
        'get_level_display',
        'supplier_link',
        'city',
        'debt',
        'created_at'
    )
    list_filter = ('city',)  # Фильтр по названию города
    search_fields = ('name', 'city', 'country')
    readonly_fields = ('created_at', 'get_level_display')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'get_level_display', 'supplier', 'debt', 'created_at')
        }),
        ('Контакты', {
            'fields': ('email', 'country', 'city', 'street', 'house_number')
        }),
        ('Продукты', {
            'fields': ('products',)
        }),
    )
    filter_horizontal = ('products',)  # Удобный виджет для выбора продуктов
    actions = [clear_debt]  # Добавляем action для очистки долга

    def supplier_link(self, obj):
        """
        Создает ссылку на страницу поставщика в админке
        """
        if obj.supplier:
            url = reverse('admin:network_networknode_change', args=[obj.supplier.id])
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"

    supplier_link.short_description = "Поставщик"

    def get_level_display(self, obj):
        """
        Отображение уровня иерархии
        """
        return obj.get_level_display()

    get_level_display.short_description = "Уровень иерархии"

    # Чтобы уровень не редактировался вручную
    readonly_fields = ('created_at', 'get_level_display')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Настройка админ-панели для модели Product
    """
    list_display = ('name', 'model', 'release_date')
    list_filter = ('release_date',)
    search_fields = ('name', 'model')
    ordering = ('name', 'model')
