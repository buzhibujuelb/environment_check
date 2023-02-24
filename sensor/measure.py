import threading
import sys
import time
from datetime import datetime
import RPi.GPIO as GPIO
from ENS160.RTrobot_ENS160 import * 
from ENS210.RTrobot_ENS210 import * 
from LTR390UV.RTrobot_LTR390UV import * 

ens210 = RTrobot_ENS210()
buf210 = ens210.ENS210_Init()

#温度和湿度
temperature1 = 0.0
humidity1 = 0.0

ENS160_MODE_I2C = 1
ENS160_MODE_SPI = 2

#空气质量
air_Data1 = 0
air_Data2 = 0
air_Data3 = 0

ens160 = RTrobot_ENS160(mode=ENS160_MODE_I2C, spi_cs=8)
buf160 = ens160.ENS160_Init()

#空气质量
light_Data1 = 0
light_Data2 = 0

ltr390 = RTrobot_LTR390UV()
buf390 = ltr390.LTR390UV_Init()

#每600秒进行一次repeat操作
def createTimer():
    t = threading.Timer(5, repeat)
    t.start()

def repeat():
    file_handle = open('./data.txt', 'a')
    file_handle.write(str(temperature1) + " " + str(humidity1) + " ")
    file_handle.write(str(air_Data1) + " " + str(air_Data2) + " " + str(air_Data3) + " ")
    file_handle.write(str(light_Data1) + " " + str(light_Data2) + "\n")

    file_handle.close()

    createTimer()

def printTime():
    tim = datetime.now()
    print(tim.strftime("%H:%M:%S"),'\t',end='')


def printData1():
    t_value, h_value = ens210.ENS210_GetMeasure()
    # 温度和湿度
    global temperature1
    global humidity1

    temperature1 = format(ens210.ENS210_Convert_Temperature(t_value), '.2f')
    humidity1 = format(ens210.ENS210_Convert_Humidity(h_value), '.2f')

    print(f"Temp: {temperature1}\tHumi: {humidity1}\t",end='')

    time.sleep(1)

def printData2():
    ens160.ENS160_measure(True, 25, 50)
    global air_Data1
    global air_Data2
    global air_Data3
    air_Data1 = ens160._data_aqi
    air_Data2 = ens160._data_tvoc
    air_Data3 = ens160._data_eco2
    print("AQI: %d\tTVOC: %dppb\teCO2: %dppm\t" % (ens160._data_aqi, ens160._data_tvoc, ens160._data_eco2),end='')
    time.sleep(1)

def printData3():

    global light_Data1, light_Data2
    if ltr390.LTR390UV_GetDataStatus() == True:
        if ltrmode == ltr390.LTR390UV_MODE_ALS:
            als = ltr390.LTR390UV_GetALS()
            lux = ltr390.LTR390UV_GetLUX(als, 1)
            print("ALS: %d\tLux: %f\r\n" % (als, lux))
            light_Data1 = als
            light_Data2 = lux
        else:
            uvs = ltr390.LTR390UV_GetUVS()
            uvi = ltr390.LTR390UV_GetUVI(uvs, 1)
            print("UVS: %d\tUVI: %f\r\n" % (uvs, uvi))
            light_Data1 = uvs
            light_Data2 = uvi
    time.sleep(0.5)

if buf210 == False:
    print("ENS210 initialize error.")
    while True:
        pass
else:
    print("ENS210 initialize register finished.")
ens210.ENS210_SetSingleMode(False)

if buf160 == False:
    print("ENS160 initialize error.")
    while buf160== False:
        pass
else:
    print("ENS160 initialize register finished.")

if buf390 == False:
    print("LTR390UV initialize error.")
    while True:
        pass
else:
    print("LTR390UV initialize register finished.")

#set mode as als
ltr390.LTR390UV_SetMode(ltr390.LTR390UV_MODE_ALS)

# set mode as uvs
#ltr.LTR390UV_SetMode(ltr.LTR390UV_MODE_UVS)

ltrmode = ltr390.LTR390UV_GetMode()
if(ltrmode == ltr390.LTR390UV_MODE_ALS):
  print("mode: ALS\r\n")
else:
  print("mode: UVS\r\n")

#set gain range as 3
ltr390.LTR390UV_SetGain(ltr390.LTR390UV_GAIN_RANGE_3)

#set measurement rate as 100ms and set resolution as 18 bit
ltr390.LTR390UV_SetMeasurement(ltr390.LTR390UV_MEASUREMENT_RATE_100MS | ltr390.LTR390UV_RESOLUTION_18BIT)

createTimer()

try:
    while True:
        printTime()
        printData1()
        printData2()
        printData3()

except KeyboardInterrupt:
    pass

GPIO.cleanup()
