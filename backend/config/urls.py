from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.catalog.views import CarViewSet
from apps.bookings.views import BookingViewSet

router = DefaultRouter()
router.register('cars', CarViewSet, basename='cars')
router.register('bookings', BookingViewSet, basename='bookings')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
