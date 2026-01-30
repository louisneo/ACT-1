from django.db import models
import datetime

class Employee(models.Model):
    first_name = models.CharField(max_length=25)
    middle_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    suffix = models.CharField(max_length=5)
    username = models.CharField(max_length=20)
    contact_number = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    position = models.CharField(max_length=25)
    birthdate = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.first_name} {self.last_name} '

                               