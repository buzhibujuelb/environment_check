#!/usr/bin/env python3

# RTrobot ENS210 Sensor Test
# http://rtrobot.org

#开机进行5次数据测试

import RTrobot_ENS210
import sys
import time
import RPi.GPIO as GPIO

ens = RTrobot_ENS210.RTrobot_ENS210()
buf = ens.ENS210_Init()

"""
if buf == False:
    print("ENS210 initialize error.")
    while True:
        pass
else:
    print("ENS210 initialize register finished.")

"""
ens.ENS210_SetSingleMode(False)

try:
    #进行5次测试
    for i in range(5):
        t_value,h_value=ens.ENS210_GetMeasure()
        #print(format(ens.ENS210_Convert_Temperature(t_value),'.2f'),format(ens.ENS210_Convert_Humidity(h_value),'.2f'),)
        #time.sleep(1)
        

except KeyboardInterrupt:
    pass
GPIO.cleanup()
