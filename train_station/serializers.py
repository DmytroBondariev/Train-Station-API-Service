from django.db import transaction
from rest_framework import serializers

from train_station.models import TrainType, Train, Station, Route, Journey, Order, Ticket


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "type", "wagon_count", "wagon_capacity", "capacity", "image")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "train", "route", "departure_time", "arrival_time", "duration")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_ticket(
            attrs["wagon_number"],
            attrs["seat_number"],
            attrs["journey"].train,
            serializers.ValidationError,
        )

    class Meta:
        model = Ticket
        fields = ("id", "journey", "seat")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order
