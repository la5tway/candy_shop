from app_couriers.serializers import CourierSerializer
from .models import Orders


class OrderSerializer(CourierSerializer):
    id_field_name = "order_id"

    class Meta:
        model = Orders
        fields = ('order_id', 'weight', 'region', 'delivery_hours', )

class SingleOrderSerializer(OrderSerializer):

    class Meta:
        model = Orders
        fields = '__all__'
        depth = 1
