from django.urls import path, include
from rest_framework import routers

from train_station.views import (
    StationViewSet,
    TrainViewSet,
    JourneyViewSet,
    OrderViewSet
)
router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "train_station"
