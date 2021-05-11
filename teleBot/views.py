import json

import requests
from django.conf import settings
from django.db import IntegrityError
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
            msg = "The Following Commands Are Allowed : \n /register : To Register For Notification \n /add : To add another pincode \n /delete : To remove pincode \n /list : To list all suscribed pin"
            self.send_message(msg, t_chat["id"])
            return JsonResponse({"ok": "POST request processed"})
        try:
            
            user = Teligram_User.objects.get(telegram_id=t_chat["id"])
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
          if user.user_subscription_data.all().count == 0:
            self.send_message("Please Enter Pin Code You Wants To Register For", t_chat["id"])
          else :
            self.send_message("You Are Already Registered .\n Click /help for more commands", t_chat["id"])

        elif text.isnumeric() and len(text) == 6:
          if user.can_delete :
            try:
              User_Subscription_Data.objects.get(user=user,pincode__pincode=text).delete()
            except User_Subscription_Data.DoesNotExist:
              self.send_message("You Havent Added this pin %s" % text,
                              t_chat["id"])
            user.can_delete=False
            user.save()
            self.send_message("You Had Unubscribed to ***%s*** \n click /list to get your added pincodes " % text,
                              t_chat["id"])
          elif user.can_add: 
            try:
                pincode = Pincode.objects.get(pincode=text)
            except Pincode.DoesNotExist:
                pincode = Pincode()
                pincode.pincode = int(text)
                pincode.save()
            user.can_add= False
            user.save()
            u_data = User_Subscription_Data()
            u_data.message_id = t_message["message_id"]
            u_data.user = user
            u_data.pincode = pincode
            try:
                u_data.save()
            except IntegrityError :
                self.send_message(
                    "You Already Had Subscribed to ***%s*** \n click /list to know your PINCODES " % text,
                    t_chat["id"])
                return JsonResponse({"ok": "POST request processed"})

            self.send_message("You Had Subscribed to ***%s*** \n we will let you know once slots available " % text,
                              t_chat["id"])
          else:
            msg = "***Unknown Command*** Please Press /help To Get Help "
            self.send_message(msg, t_chat["id"])

        elif text == "add":
            user.can_add=True
            user.save()
            self.send_message("Please Enter Different Pin Code", t_chat["id"])

        elif text == "list":
            u_data = user.user_subscription_data.all()
            msg = "You Had Registered For following Pincodes :\n"+"\n".join([str(pin.pincode.pincode) for pin in u_data])
            self.send_message(msg, t_chat["id"])
        
        elif text == "delete":
            user.can_delete=True
            user.save()
            self.send_message("Please Enter Pin Code You Want to remove", t_chat["id"])
        elif text == "deregister":
            user.deregister=True
            user.save()
            self.send_message("You Have Been deregister,\n If changed your mind click", t_chat["id"])
            
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
