from .fetch_availaibility import *
import time
sleeptime = 1 

while sleeptime>0:
  time.sleep(10)
  print(get_cowin_data())
  sleeptime=0