from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, APIException
from autorent_core.exceptions import AutoRentError, BookingConflict
from autorent_core.rules import BookingState
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer
from .services import BookingService


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Конфлікт періоду бронювання.'


class BookingViewSet(viewsets.GenericViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.select_related('car', 'user')

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def create(self, request):
        data = BookingCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        try:
            booking = BookingService().create(
                user=request.user, car_id=values['car_id'],
                starts_at=values['starts_at'], ends_at=values['ends_at'],
            )
        except BookingConflict as e:
            raise Conflict(str(e)) from e
        except AutoRentError as e:
            raise ValidationError({'detail': str(e)}) from e
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my')
    def my(self, request):
        qs = self.queryset.filter(user=request.user).order_by('-created_at')
        return Response(self.get_serializer(qs, many=True).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        try:
            booking = BookingService().cancel_for_client(user=request.user, booking_id=int(pk))
        except AutoRentError as e:
            raise ValidationError({'detail': str(e)}) from e
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'], url_path='manager-cancel')
    def manager_cancel(self, request, pk=None):
        try:
            booking = BookingService().move_by_manager(
                manager=request.user, booking_id=int(pk),
                next_state=BookingState.CANCELLED,
                reason=str(request.data.get('reason', '')),
            )
        except AutoRentError as e:
            raise ValidationError({'detail': str(e)}) from e
        except ValueError as e:
            raise ValidationError({'reason': str(e)}) from e
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        return self._manager_transition(request, pk, BookingState.ACTIVE)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        return self._manager_transition(request, pk, BookingState.COMPLETED)

    def _manager_transition(self, request, pk, state):
        try:
            booking = BookingService().move_by_manager(
                manager=request.user, booking_id=int(pk), next_state=state,
            )
        except AutoRentError as e:
            raise ValidationError({'detail': str(e)}) from e
        return Response(self.get_serializer(booking).data)
