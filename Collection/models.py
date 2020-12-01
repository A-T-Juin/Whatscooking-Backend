from django.db import models
from django.conf import settings

class Collection(models.Model):
    name = models.CharField(max_length=15, blank=False)
    info = models.TextField(blank=True)
    owned_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='collections', on_delete=models.CASCADE)
    # Has a m2m field of recipes
