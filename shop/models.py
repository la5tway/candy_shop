from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import validate_comma_separated_integer_list, MinValueValidator, MaxValueValidator
from rest_framework.exceptions import ValidationError

User = get_user_model()

COURIER_TYPES = (
    ('foot', 'foot'),
    ('bike', 'bike'),
    ('car', 'car')
)

WEIGHT_MAP = {
    'foot': 10,
    'bike': 15,
    'car': 50
}
class Couriers(models.Model):

    courier_id = models.PositiveIntegerField(primary_key=True, verbose_name='Номер курьера')
    courier_type = models.CharField(verbose_name='Тип передвижения',  choices=COURIER_TYPES, max_length=32)
    regions = models.JSONField(default=list)
    working_hours = models.JSONField(default=list)
    # free_working_hours = models.JSONField(default=list)
    # rating = models.FloatField(verbose_name='Рейтинг курьера', default=0)
    earnings = models.PositiveIntegerField(verbose_name='Заработок курьера', default=0)

    class Meta:
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'

    def __str__(self):
        return f'Курьер: {self.courier_id}'

class Orders(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True, verbose_name='Номер заказа')
    weight = models.DecimalField(
        verbose_name='Вес заказа',
        max_digits=4,
        decimal_places=2
    )
    region = models.PositiveIntegerField(blank=True, null=True, verbose_name='Регион')
    delivery_hours = models.JSONField(verbose_name='Часы работы', default=list)
    time_of_delivered = models.DateTimeField(verbose_name="ДТ доставки", blank=True, null=True)
    courier = models.ForeignKey(
        verbose_name="Курьер",
        to=Couriers,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders"
    )
    is_delivered = models.BooleanField(verbose_name="Доставлено?", default=False)
    courier_type = models.CharField(verbose_name='Тип курьера',  choices=COURIER_TYPES, max_length=32, blank=True, null=True)
    time_of_assign = models.DateTimeField(verbose_name="ДТ принятия заказа в работу", blank=True, null=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ: {self.order_id}'
