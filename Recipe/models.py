from django.db import models
from Collection.models import Collection
from django.conf import settings

class Recipe(models.Model):
    DIFFICULTY_LEVELS = [
        ('E', 'Easy'),
        ('F', 'Fair'),
        ('H', 'Hard'),
        ('C', 'Challenging')
    ]
    name = models.CharField(max_length=50, blank=False)
    image = models.TextField(blank=False)
    tags = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=False)
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_LEVELS, blank=False)
    ingredients = models.TextField(max_length=30, blank=False)
    time = models.IntegerField(blank=False)
    servings = models.IntegerField(blank=False)
    in_collection = models.ManyToManyField(Collection, related_name='recipes',symmetrical=False, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recipes', on_delete=models.CASCADE)
    created_date = models.DateField(auto_now=True)
    # Has a foreign key field of steps

    @property
    def amount_of_likes(self):
        # This will call the amount of likes that the recipe has
        total_likes = 0
        for steps in self.steps.all():
            total_likes += len(steps.likes.all())
        return total_likes

    @property
    def total_comments(self):
        number_of_comments = 0
        for steps in self.steps.all():
            number_of_comments += steps.amount_of_comments
        return number_of_comments

    @property
    def difficulty_level(self):
        # This will call the difficulty level in a readable form
        return self.get_difficulty_display()
