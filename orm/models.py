from django.db import models

# Create your models here.


class Tips(models.Model):
    key = models.CharField(max_length=3)
    value = models.CharField(max_length=255)
