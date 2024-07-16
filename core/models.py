from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    organization = models.ForeignKey('Organization', null=True, blank=True, on_delete=models.SET_NULL)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('developer', 'Developer'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')

class Organization(models.Model):
    name = models.CharField(max_length=255)
    invite_code = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Cluster(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    total_ram = models.IntegerField()
    total_cpu = models.IntegerField()
    total_gpu = models.IntegerField()
    available_ram = models.IntegerField()
    available_cpu = models.IntegerField()
    available_gpu = models.IntegerField()

    def __str__(self):
        return self.name


class Deployment(models.Model):
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    docker_image_path = models.CharField(max_length=255)
    required_ram = models.IntegerField()
    required_cpu = models.IntegerField()
    required_gpu = models.IntegerField()
    priority = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')

    def __str__(self):
        return f'{self.user} - {self.cluster}'
