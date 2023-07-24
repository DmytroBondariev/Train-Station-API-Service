import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


class TrainType(models.Model):
    TRAIN_TYPE_CHOICES = (
        ("Long-distance", "Long-distance"),
        ("Express", "Express"),
        ("Regional", "Regional"),
        ("Inter-City", "Inter-City")
    )
    name = models.CharField(
        choices=TRAIN_TYPE_CHOICES,
        max_length=63,
        unique=True
    )

    def __str__(self):
        return self.name


def train_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/trains/", filename)


class Train(models.Model):
    name = models.CharField(max_length=63)
    type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )
    wagon_count = models.IntegerField()
    wagon_capacity = models.IntegerField()
    image = models.ImageField(null=True, upload_to=train_image_file_path)

    @property
    def capacity(self):
        return self.wagon_count * self.wagon_capacity

    def __str__(self):
        return self.name


def station_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/stations/", filename)


class Station(models.Model):
    name = models.CharField(max_length=63)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(null=True, upload_to=station_image_file_path)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="source"
    )
    destination = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="destination"
    )

    @property
    def distance(self):
        return int(
            (
                    (self.source.latitude - self.destination.latitude) ** 2 +
                    (
                            self.source.longitude - self.destination.longitude
                    ) ** 2) ** 0.5
        )

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class Journey(models.Model):
    train = models.ForeignKey(
        Train,
        on_delete=models.CASCADE,
        related_name="journeys"
    )
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE,
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


    def __str__(self):
        return f"{self.train.name} {self.route.source.name} - " \
               f"{self.route.destination.name} {self.departure_time} - " \
               f"{self.arrival_time}"

    class Meta:
        ordering = ["departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def str(self):
        return f"{self.created_at}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="tickets")
    wagon_number = models.IntegerField()
    seat_number = models.IntegerField()

    @staticmethod
    def validate_ticket(wagon_number, seat_number, journey, error_to_raise):
        if wagon_number < 1 or wagon_number > journey.train.wagon_count:
            raise error_to_raise(
                {
                    "wagon_number": f"Wagon number must be in available range: "
                                    f"(1, {journey.train.wagon_count})"
                }
            )
        if seat_number < 1 or seat_number > journey.train.wagon_capacity:
            raise error_to_raise(
                {
                    "seat_number": f"Seat number must be in available range: "
                                   f"(1, {journey.train.wagon_capacity})"
                }
            )

    def clean(self):
        self.validate_ticket(
            self.wagon_number, self.seat_number, self.journey, ValidationError
        )

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.validate_ticket(
            self.wagon_number, self.seat_number, self.journey, ValueError
        )
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.journey} {self.wagon_number} {self.seat_number}"

    class Meta:
        unique_together = ("journey", "wagon_number", "seat_number")
        ordering = ["journey", "wagon_number", "seat_number"]
