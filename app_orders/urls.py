from django.urls import path
from .views import (
    OrdersView,
    SingleOrdersView,
    OrdersAssign,
    OrderComplete,
)


app_name = 'app_orders'


urlpatterns = [
    path('', OrdersView.as_view()),
    path('<int:pk>', SingleOrdersView.as_view()),
    path('assign', OrdersAssign.as_view()),
    path('complete', OrderComplete.as_view()),
]
