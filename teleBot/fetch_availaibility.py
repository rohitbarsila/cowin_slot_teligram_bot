from datetime import datetime

import requests

from .models import Pincode

date = datetime.now().date().strftime("%d-%m-%Y")


def get_cowin_data():
    centers = ""
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin"
    headers = {
        'user-agent': 'hjk',
    }
    pincodes = Pincode.objects.all()
    for pincode in pincodes:
        params = (
            ('pincode', pincode.pincode),
            ('date', date),
        )

        response = requests.get(URL, headers=headers, params=params)
        for center in response.json()['centers']:

            for sessions in center['sessions']:
                if sessions['min_age_limit'] == 18 and sessions['available_capacity'] > 0:
                    pincode.raw = response.json()
                    pincode.slot_status = True
                    pincode.save()
                    centers += "Date : " + sessions["date"] + ", Total Slots : " + str(
                        sessions['available_capacity']) + "\nVaccine Name " + sessions['vaccine'] + " \n" + center[
                                   'name'] + " \n" + center['address'] + "For Cost : " + \
                               center['fee_type'] + "\n\n"
    msg = "Cheers! Just Found Total Slot Available In Your PinCode " + str(
        pincode.pincode) + " \nHere Are Details \n\n" + centers + "***BOOK ASAP***"
    pincode.send_slot_msg(msg)
    return True
