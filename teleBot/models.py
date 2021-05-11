import requests
from django.conf import settings
from django.db import models


# Create your models here.


class Teligram_User(models.Model):
    telegram_id = models.IntegerField(unique=True, db_index=True)
    name = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20)
    can_add = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=False)
    deregister = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.telegram_id)



class Pincode(models.Model):
    pincode = models.IntegerField(blank=True, null=True)
    slot_status = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def send_slot_msg(self, text):
        data = {
            "chat_id": self.user_subscription_data.get().user.telegram_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{settings.TELEGRAMBOT_URL}{settings.TELEGRAMBOT_TOKEN}/sendMessage", data=data
        )
        return True

    def __str__(self):
        return str(self.pincode)


class User_Subscription_Data(models.Model):
    message_id = models.IntegerField(unique=True, db_index=True)
    user = models.ForeignKey(Teligram_User, on_delete=models.CASCADE, related_name="user_subscription_data")
    pincode = models.ForeignKey(Pincode, on_delete=models.CASCADE, related_name="user_subscription_data", null=True,
                                blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.message_id)

    class Meta:
        unique_together = ('user', 'pincode',)
