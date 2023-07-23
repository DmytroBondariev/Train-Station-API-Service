from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from train_station.models import TrainType


@receiver(post_migrate)
def create_train_types(sender, **kwargs):
    if sender.name == 'train_station':
        TrainType.objects.all().delete()

        for choice in TrainType.TRAIN_TYPE_CHOICES:
            TrainType.objects.create(name=choice[0])
