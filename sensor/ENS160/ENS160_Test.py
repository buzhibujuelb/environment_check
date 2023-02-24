#!/usr/bin/env python3

# RTrobot ENS160 Sensor Test
# http://rtrobot.org
# SPI use spi0


import RTrobot_ENS160
import sys
import time
import RPi.GPIO as GPIO

ENS160_MODE_I2C = 1
ENS160_MODE_SPI = 2

ens = RTrobot_ENS160.RTrobot_ENS160(mode=ENS160_MODE_I2C, spi_cs=8)
buf = ens.ENS160_Init()
if buf == False:
    print("ENS160 initialize error.")
    while buf== False:
        pass
else:
    print("ENS160 initialize register finished.")

try:
    while True:
        ens.ENS160_measure(True, 25, 50)
        print("AQI:%d\tTVOC:%dppb\teCO2:%dppm\r\n"%(ens._data_aqi,ens._data_tvoc,ens._data_eco2))
        time.sleep(1)
except KeyboardInterrupt:
    pass
GPIO.cleanup()
