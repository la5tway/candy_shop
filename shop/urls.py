from django.urls import path
from .views import (
    CouriersView,
    SingleCouriersView,
    OrdersView,
    SingleOrdersView,
    OrdersAssign,
    OrderComplete
)
app_name = 'candy_shop'


# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('couriers/', CouriersView.as_view()),
    path('orders/', OrdersView.as_view()),
    path('couriers/<int:pk>', SingleCouriersView.as_view()),
    path('orders/<int:pk>', SingleOrdersView.as_view()),
    path('orders/assign', OrdersAssign.as_view()),
    path('orders/complete', OrderComplete.as_view()),
]
