from datetime import datetime

from django.db.models import Count, F
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from train_station.models import Station, Train, Journey
from train_station.permissions import IsAdminOrIfAuthenticatedReadOnly
from train_station.serializers import StationSerializer, TrainSerializer, JourneySerializer, JourneyListSerializer, \
    JourneyDetailSerializer


class StationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().prefetch_related(
        "train", "route"
    ).annotate(
        tickets_available=(F("train__wagon_count") * F("train__wagon_capacity")) - Count("tickets"))
    serializer_class = JourneySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date", None)
        source = self.request.query_params.get("source", None)
        destination = self.request.query_params.get("destination", None)
        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)
        if source and destination:
            queryset = queryset.filter(route_source__in=source, route_destination__in=destination)

            return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer
