from django.db import models
from django.conf import settings
from Step.models import Step

class Comment(models.Model):
    text = models.CharField(max_length=250, blank=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
    replying_to = models.ForeignKey('self', related_name='responses', on_delete=models.CASCADE, null=True, blank=True)
    step_comment = models.ForeignKey(Step, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateField(auto_now=True)
    # Has a Foreignkey field of responses
