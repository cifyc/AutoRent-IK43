from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Car
from .serializers import CarSerializer

class CarViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CarSerializer
    permission_classes = [AllowAny]
    queryset = Car.objects.filter(is_published=True).order_by('id')

    def get_queryset(self):
        qs = super().get_queryset()
        city = self.request.query_params.get('city')
        category = self.request.query_params.get('category')
        if city:
            qs = qs.filter(city__iexact=city)
        if category:
            qs = qs.filter(category__iexact=category)
        return qs
