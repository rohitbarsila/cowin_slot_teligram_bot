import json

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from .models import Teligram_User, User_Subscription_Data, Pincode


TELEGRAM_URL = "https://api.telegram.org/bot"
TUTORIAL_BOT_TOKEN = settings.TELEGRAMBOT_TOKEN


class WebHook(View):

    def post(self, request, *args, **kwargs):
        t_data = json.loads(request.body)
        try:
          t_message = t_data["message"]
          t_chat = t_message["chat"]
        except :
          pass

        try:
            text = t_message["text"].strip().lower()
            text = text.lstrip("/")
        except Exception as e:
            return JsonResponse({"ok": "POST request processed"})

        user = ""
        if text == "help":
            msg = "The Following Commands Are Allowed : \n\n /register : To Register For Notification \n /edit : To change the existing pincode "
            self.send_message(msg, t_chat["id"])
            return JsonResponse({"ok": "POST request processed"})
        try:
            user = Teligram_User.objects.get(telegram_id=t_chat["id"])
            if user.validate_data() and text != "edit":
                msg = "***Thanks*** \n\n You Are Already Registered \n Please click for /help"
                self.send_message(msg, t_chat["id"])
                return JsonResponse({"ok": "POST request processed"})
        except Teligram_User.DoesNotExist:
            t_user = Teligram_User()
            t_user.telegram_id = t_chat["id"]
            t_user.name = t_chat["first_name"]
            t_user.username = t_chat["first_name"]+" "+t_chat["last_name"]
            t_user.account_type = t_chat["type"]
            t_user.save()

            self.send_message("Your New PinCode is ***%s*** \n we will let you know once slots available " % text,
                              t_chat["id"])

        if text == "start":
            msg = "***Welcome*** \n\n To Register For Notification \n Please click /register"
            self.send_message(msg, t_chat["id"])

        elif text == "register":
            try:
                u_data = User_Subscription_Data.objects.get(user__telegram_id=t_chat["id"])
            except User_Subscription_Data.DoesNotExist:
                u_data = User_Subscription_Data()
                u_data.message_id = t_message["message_id"]
                u_data.user = user
                u_data.save()
            self.send_message("Please Enter Pin Code You Wants To Register For", t_chat["id"])

        elif text.isnumeric() and len(text) == 6:
            try:
                pincode = Pincode.objects.get(pincode=text)
            except Pincode.DoesNotExist:
                pincode = Pincode()
                pincode.pincode = int(text)
                pincode.save()
            try:
              u_data = User_Subscription_Data.objects.get(user__telegram_id=t_chat["id"])
              u_data.can_modify = False
              u_data.pincode = pincode
              u_data.save()
            except User_Subscription_Data.DoesNotExist:
              self.send_message("Some Issue Please Register Again\n if not solving connect @rohitbarsila",
                              t_chat["id"])
            
            self.send_message("You Had Subscribed to ***%s*** \n we will let you know once slots available " % text,
                              t_chat["id"])

        elif text == "edit":
            u_data = user.user_subscription_data.get()
            u_data.can_modify = True
            u_data.save()
            self.send_message("Please Enter New Pin Code", t_chat["id"])

        else:
            msg = "***Unknown Command*** Please Press /help To Get Help "
            self.send_message(msg, t_chat["id"])

        return JsonResponse({"ok": "POST request processed"})

    @staticmethod
    def send_message(message, chat_id):
        data = {
            "chat_id": [chat_id],
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TUTORIAL_BOT_TOKEN}/sendMessage", data=data
        )
