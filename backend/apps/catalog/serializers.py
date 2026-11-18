from rest_framework import serializers
from .models import Car

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'category', 'city', 'seats', 'image_url', 'daily_rate_uah', 'deposit_uah']
