#!/usr/bin/env python3

# RTrobot LTR390UV Sensor Test
# http://rtrobot.org

import RTrobot_LTR390UV
import sys
import time
import RPi.GPIO as GPIO


ltr = RTrobot_LTR390UV.RTrobot_LTR390UV()
buf = ltr.LTR390UV_Init()
if buf == False:
    print("LTR390UV initialize error.")
    while True:
        pass
else:
    print("LTR390UV initialize register finished.")

#set mode as als
ltr.LTR390UV_SetMode(ltr.LTR390UV_MODE_ALS)

# set mode as uvs
#ltr.LTR390UV_SetMode(ltr.LTR390UV_MODE_UVS)

ltrmode = ltr.LTR390UV_GetMode()
if (ltrmode == ltr.LTR390UV_MODE_ALS):
	print("mode: ALS\r\n")
else:
	print("mode: UVS\r\n")

#set gain range as 3
ltr.LTR390UV_SetGain(ltr.LTR390UV_GAIN_RANGE_3);

#set measurement rate as 100ms and set resolution as 18 bit
ltr.LTR390UV_SetMeasurement(ltr.LTR390UV_MEASUREMENT_RATE_100MS | ltr.LTR390UV_RESOLUTION_18BIT)

#Set the upper and lower interrupt limits
#range: 0 - 1048575
#ltr.LTR390UV_SetThresholds(20, 500)

#Set the interrupt type and interrupt trigger threshold count
#ltr.LTR390UV_SetInterrupt(True, ltr.LTR390UV_INT_UVS, ltr.LTR390UV_PST_EVERY)

try:
    while True:
        if ltr.LTR390UV_GetDataStatus() == True:
            if ltrmode == ltr.LTR390UV_MODE_ALS:
                als = ltr.LTR390UV_GetALS()
                lux = ltr.LTR390UV_GetLUX(als,1)
                print("ALS: %d,\tLux: %f\r\n" %(als,lux))
            else:
                uvs = ltr.LTR390UV_GetUVS()
                uvi = ltr.LTR390UV_GetUVI(uvs,1)
                print("UVS: %d,\tUVI: %f\r\n" %(uvs,uvi))
        time.sleep(0.5)

except KeyboardInterrupt:
    pass
GPIO.cleanup()
