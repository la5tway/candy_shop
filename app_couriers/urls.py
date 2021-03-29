from django.urls import path
from .views import (
    CouriersView,
    SingleCouriersView
)


app_name = 'app_couriers'


urlpatterns = [
    path('', CouriersView.as_view()),
    path('<int:pk>', SingleCouriersView.as_view()),
]
