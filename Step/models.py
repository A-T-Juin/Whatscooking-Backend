from django.db import models
from django.conf import settings
from Recipe.models import Recipe

class Step(models.Model):
    name = models.CharField(max_length=50, blank=False)
    image = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    of_recipe = models.ForeignKey(Recipe, related_name='steps', on_delete=models.CASCADE)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', symmetrical=False, blank=True)
    position = models.IntegerField(blank=True, default=0)
    # Has a foreignkey field of comments

    class Meta:
        ordering = ["position"]

    @property
    def amount_of_comments(self):
        return len(self.comments.all())

    @property
    def amount_of_likes(self):
        return len(self.likes.all())
