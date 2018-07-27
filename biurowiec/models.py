from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=128)
    capacity = models.IntegerField()
    has_projector = models.BooleanField()


class Reservation(models.Model):
    date = models.DateField()
    comment = models.TextField(null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
