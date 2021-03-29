from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/couriers/', include('app_couriers.urls')),
    path('api/orders/', include('app_orders.urls')),
]
