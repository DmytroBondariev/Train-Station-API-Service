from django.apps import AppConfig


class TrainStationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "train_station"

    def ready(self):
        import train_station.signals
