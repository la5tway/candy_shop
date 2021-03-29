from django.db import models
from app_couriers.models import Couriers, COURIER_TYPES


class Orders(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True, verbose_name='Номер заказа')
    weight = models.FloatField(
        verbose_name='Вес заказа'
    )
    region = models.PositiveIntegerField(blank=True, null=True, verbose_name='Регион')
    delivery_hours = models.JSONField(verbose_name='Интервал времени доставки', default=list)
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
