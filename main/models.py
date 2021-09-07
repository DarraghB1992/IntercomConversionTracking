from django.db import models


# Create your models here.
class Conversation(models.Model):
    conversation_id = models.IntegerField()
    conversation_created_at = models.DateTimeField()
    conversation_closed_at = models.DateTimeField()

    intercom_user_id = models.CharField(max_length=50)
    intercom_user_name = models.CharField(max_length=50)
    intercom_user_email = models.EmailField()

    teammate_id = models.CharField(max_length=50)
    teammate_name = models.CharField(max_length=50)
    teammate_email = models.EmailField()

    conversation_impacted_sale = models.BooleanField(default=False)
    def __str__(self):
        return str(self.conversation_id)

