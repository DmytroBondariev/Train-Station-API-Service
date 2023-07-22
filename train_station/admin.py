from django.contrib import admin

from train_station.models import Station, Train, TrainType, Route, Journey, Order, Ticket

admin.site.register(Station)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Route)
admin.site.register(Journey)
admin.site.register(Order)
admin.site.register(Ticket)
