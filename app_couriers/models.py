from django.db import models

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
    earnings = models.PositiveIntegerField(verbose_name='Заработок курьера', default=0)

    class Meta:
        verbose_name = 'Курьер'
        verbose_name_plural = 'Курьеры'

    def __str__(self):
        return f'Курьер: {self.courier_id}'
