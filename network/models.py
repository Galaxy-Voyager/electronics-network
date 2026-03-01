from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    """
    Модель продукта, который продает звено сети
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    model = models.CharField(max_length=255, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ['name', 'model']

    def __str__(self):
        return f"{self.name} - {self.model}"


class NetworkNode(models.Model):
    """
    Модель звена сети (завод, розничная сеть, ИП)
    """

    # Уровни иерархии (для удобства, но уровень вычисляется автоматически)
    class Level(models.IntegerChoices):
        FACTORY = 0, 'Завод'
        RETAIL_NETWORK = 1, 'Розничная сеть'
        INDIVIDUAL_ENTREPRENEUR = 2, 'Индивидуальный предприниматель'

    # Название звена
    name = models.CharField(max_length=255, verbose_name="Название", unique=True)

    # Контакты
    email = models.EmailField(max_length=255, verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=100, verbose_name="Улица")
    house_number = models.CharField(max_length=20, verbose_name="Номер дома")

    # Продукты (связь многие ко многим, так как одно звено может продавать много продуктов,
    # и один продукт может продаваться во многих звеньях)
    products = models.ManyToManyField(Product, related_name='network_nodes', verbose_name="Продукты")

    # Поставщик (ссылка на другое звено сети)
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name="Поставщик",
        help_text="Предыдущее по иерархии звено сети"
    )

    # Задолженность перед поставщиком
    debt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Задолженность перед поставщиком",
        help_text="В денежном выражении с точностью до копеек"
    )

    # Время создания
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_level_display()} - {self.name}"

    def get_level(self):
        """
        Вычисляет уровень иерархии звена
        0 - завод (нет поставщика)
        1 - розничная сеть (поставщик - завод)
        2 - ИП (поставщик - розничная сеть или завод)
        и так далее...
        """
        level = 0
        current = self
        while current.supplier:
            level += 1
            current = current.supplier
            if level > 10:  # Защита от бесконечного цикла
                break
        return level

    def get_level_display(self):
        """
        Возвращает текстовое представление уровня
        """
        level = self.get_level()
        if level == 0:
            return "Завод"
        elif level == 1:
            return "Розничная сеть"
        elif level == 2:
            return "Индивидуальный предприниматель"
        else:
            return f"Звено {level} уровня"
