from django.db import models


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


class Train(models.Model):
    name = models.CharField(max_length=63)
    type = models.ForeignKey(
        TrainType,
        on_delete=models.CASCADE,
        related_name="trains"
    )
    wagon_count = models.IntegerField()
    wagon_capacity = models.IntegerField()

    @property
    def capacity(self):
        return self.wagon_count * self.wagon_capacity

    def __str__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=63)
    latitude = models.FloatField()
    longitude = models.FloatField()

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

    @property
    def duration(self):
        return self.arrival_time - self.departure_time

    def __str__(self):
        return f"{self.train.name} {self.route.source.name} - " \
               f"{self.route.destination.name} {self.departure_time} - " \
               f"{self.arrival_time}"
