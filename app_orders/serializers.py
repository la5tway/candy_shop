from rest_framework import serializers
from app_couriers.serializers import CourierSerializer
from .models import Orders


class OrderSerializer(CourierSerializer):
    id_field_name = "order_id"
    # weight = serializers.DecimalField(
    #     max_digits=4, decimal_places=2, min_value=0.01, max_value=50
    # )
    class Meta:
        model = Orders
        fields = ('order_id', 'weight', 'region', 'delivery_hours', )

class OrderAllSerializer(OrderSerializer):

    class Meta:
        model = Orders
        fields = '__all__'
        depth = 1
