from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    car_title = serializers.CharField(source='car.__str__', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'number', 'car', 'car_title', 'starts_at', 'ends_at', 'status',
            'daily_rate_snapshot_uah', 'billable_days', 'total_uah',
            'deposit_snapshot_uah', 'created_at',
        ]

class BookingCreateSerializer(serializers.Serializer):
    car_id = serializers.IntegerField(min_value=1)
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()
    terms_accepted = serializers.BooleanField()

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError('Потрібно прийняти умови оренди.')
        return value
