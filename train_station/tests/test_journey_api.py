from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from train_station.models import Journey, Station, Train, Route, TrainType
from train_station.serializers import JourneyListSerializer, JourneyDetailSerializer

JOURNEY_URL = reverse("train_station:journey-list")


def format_datetime(datetime_str):
    # Convert the datetime string to the format used by the serializer
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def sample_train(**params):
    defaults = {
        "name": "Test Train 1",
        "type": TrainType.objects.get(name="Long-distance"),
        "wagon_count": 10,
        "wagon_capacity": 50,

    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Test Station 1",
        "latitude": 1.0,
        "longitude": 1.0,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(),
        "destination": sample_station(name="Test Station 2"),
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_journey(**params):
    defaults = {
        "train": sample_train(),
        "route": sample_route(),
        "departure_time": "2024-01-01 12:00:00",
        "arrival_time": "2024-02-01 13:00:00",
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)


def detail_url(journey_id):
    return reverse("train_station:journey-detail", args=[journey_id])


class UnauthenticatedJourneyApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(JOURNEY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_journeys(self):
        sample_journey()
        sample_journey(departure_time="2024-01-01 14:00:00")

        response = self.client.get(JOURNEY_URL)

        for journey_data in response.data:
            journey_data.pop('tickets_available', None)

        journeys = Journey.objects.order_by("id")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_journeys_by_date(self):
        sample_journey()
        sample_journey(departure_time="2024-01-01 14:00:00")

        response = self.client.get(JOURNEY_URL, {"date": "2024-01-01"})

        for journey_data in response.data:
            journey_data.pop('tickets_available', None)

        journeys = Journey.objects.filter(departure_time__date="2024-01-01")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_journey_detail(self):
        journey = sample_journey()

        url = detail_url(journey.id)
        response = self.client.get(url)

        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer_data_formatted = {
            **serializer.data,
            'departure_time': response.data['departure_time'],
            'arrival_time': response.data['arrival_time'],
        }

        self.assertEqual(response.data, serializer_data_formatted)

    def test_create_journey_forbidden(self):
        """Test that authenticated user cannot create a journey"""
        payload = {
            "train": sample_train().id,
            "route": sample_route().id,
            "departure_time": "2024-01-01 12:00:00",
            "arrival_time": "2024-02-01 13:00:00",
        }

        response = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
