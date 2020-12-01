from django.db import models
# from django.contrib.auth.models import User as BaseModel, UserManager
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    info = models.TextField(max_length=250, blank=True)
    image = models.TextField(blank=True)
    following = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True)
    # Has a m2m field of followers
    # Has a foreign key field of collections
    # Has a foreign key field of comments
    # Has a foreign key field of recipes
    # Has a m2m field of likes
    # to create user User.objects._create_user(username, email, password, **kwargs)

    @property
    def amount_of_followers(self):
        # returns the amount of followers
        return len(self.followers.all())

    @property
    def amount_of_users_following(self):
        # returns the amount of users being followed
        return len(self.following.all())
