from django.db import models

# Create your models here.


class Dataset(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.CharField(max_length=10)
    channel = models.CharField(max_length=16)
    country = models.CharField(max_length=10)
    os = models.CharField(max_length=10)
    impressions = models.IntegerField(null=True)
    clicks = models.IntegerField(null=True)
    installs = models.IntegerField()
    spend = models.FloatField(null=True, blank=True)
    revenue = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.channel
