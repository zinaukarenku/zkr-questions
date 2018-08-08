from django.db import models
import random
import string

from django.contrib.auth.models import User

# Create your models here.

class Registree(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=40)
