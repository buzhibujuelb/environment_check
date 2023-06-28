import threading
import sys
import time
from datetime import datetime
import RPi.GPIO as GPIO
from ENS160.RTrobot_ENS160 import * 
from ENS210.RTrobot_ENS210 import * 
from LTR390UV.RTrobot_LTR390UV import *
import numpy as np

import psycopg2 ##导入

## 通过connect方法，创建连接对象 conn
## 这里连接的是本地的数据库
conn = psycopg2.connect(database="sensordata", user="postgres",
 password="3.1415926", host="127.0.0.1", port="5432")

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()


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

'''
ens160 = RTrobot_ENS160(mode=ENS160_MODE_I2C, spi_cs=8)
buf160 = ens160.ENS160_Init()
'''

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
    print()
    printTime()
    printData1()
    #printData2()
    printData3()

    global temperature1
    #temperature1 = -2.0
    #合法数据，正常写入数据库
    if(testDataLegal()):
        #当前时间
        tim = datetime.now()
        # 插入数据到sensor1表
        cursor.execute('''INSERT INTO SENSOR1(tistamp, temp, humi) VALUES (%f,%f,%f)''' %(float(tim.timestamp()),float(temperature1),float(humidity1)))

        conn.commit()
        print("Records inserted........ SENSOR1")

        #插入数据到sensor2表
        cursor.execute('''INSERT INTO SENSOR2(tistamp, als, lux) VALUES (%f,%f,%f)''' %(float(tim.timestamp()),float(light_Data1),float(light_Data2)))
        
        conn.commit()
        print("Records inserted........ SENSOR2")


        # Closing the connection
        #不需要关闭，control + c就关了
        #conn.close()

    #不合法的数据，写入不合法数据库
    else:
        
        tim = datetime.now()
        cursor.execute('''INSERT INTO SENSORERRORDATA(tistamp, temp, humi,als,lux) VALUES (%f,%f,%f,%f,%f)''' %(float(tim.timestamp()),float(temperature1),float(humidity1),float(light_Data1),float(light_Data2)))
        conn.commit()
        print("Records inserted........ SENSORERRORDATA")


    createTimer()

'''
def averageDate():

    #not use average as global
    #global averageTem,averageHum,averageAir1,averageAir2,averageAir3,averageLight1,averageLight2
    # 平均数据
    averageTem = 0.0
    averageHum = 0.0
    averageAir1 = 0
    averageAir2 = 0
    averageAir3 = 0
    averageLight1 = 0
    averageLight2 = 0

    #how many lines to calculate average
    lineNum = 0

    file_handle = open('./dataLess.txt', 'r')

    while True:
        # Get next line from file
        line = file_handle.readline()

        # If line is empty then end of file reached
        if not line:
            break

        if line == '':
            continue

        if line == ' ':
            continue

        #转化成列表形式
        lineList = line.split()

        #计算平均值
        averageTem += float(lineList[0])
        averageHum += float(lineList[1])
        averageAir1 += float(lineList[2])
        averageAir2 += float(lineList[3])
        averageAir3 += float(lineList[4])
        averageLight1 += float(lineList[5])
        averageLight2 += float(lineList[6])

        lineNum += 1

    print("Average:\t")
    name = ["Temerature", "Humidity", "AQI", "TVOC", "eCO2", "Als", "uvi"]
    for item in name:
        print('%-15s\t' % item, end='')

    # 平均值取两位小数
    averageArr = np.array([averageTem / lineNum, averageHum / lineNum, averageAir1 / lineNum
                              , averageAir2 / lineNum, averageAir3 / lineNum, averageLight1 / lineNum,
                           averageLight2 / lineNum])

    averageArrTwoDec = np.around(averageArr, decimals=2)

    print()
    for oneAverage in averageArrTwoDec:
        print('%-15s\t' % oneAverage, end='')

    print()
    file_handle.close()
'''

#合法返回1，不合法返回0
def testDataLegal():
    #print(temperature1)
    if(temperature1 > 45.0 or temperature1 < 0.0):
        print("temperature ERROR")
        return 0
    if(humidity1 > 100.0 or humidity1 < 10.0):
        print("humidity ERROR---------")
        return 0
    if(light_Data1 > 100.0 or light_Data1 < 0.0):
        print("als ERROR--------")
        return 0
    if(light_Data2 > 30000.0 or light_Data2 < 0.0):
        print("lux ERROR-------")
        return 0
    return 1


def printTime():
    tim = datetime.now()
    #print(tim.strftime("%H:%M:%S"),'\t',end='')
    #print(tim)
    print(tim.timestamp(),'\t',end='')

def printData1():
    t_value, h_value = ens210.ENS210_GetMeasure()
    # 温度和湿度
    global temperature1
    global humidity1

    temperature1 = float(format(ens210.ENS210_Convert_Temperature(t_value), '.2f'))
    humidity1 = float(format(ens210.ENS210_Convert_Humidity(h_value), '.2f'))

    print(f"Temp: {temperature1}\tHumi: {humidity1}\t",end='')

    time.sleep(1)

'''
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
'''

def printData3():

    global light_Data1, light_Data2
    if ltr390.LTR390UV_GetDataStatus() == True:
        if ltrmode == ltr390.LTR390UV_MODE_ALS:
            als = ltr390.LTR390UV_GetALS()
            lux = ltr390.LTR390UV_GetLUX(als, 1)
            print("ALS: %d\tLux: %f\r\n" % (als, lux))
            light_Data1 = float(als)
            light_Data2 = float(round(lux,2))
        else:
            uvs = ltr390.LTR390UV_GetUVS()
            uvi = ltr390.LTR390UV_GetUVI(uvs, 1)
            print("UVS: %d\tUVI: %f\r\n" % (uvs, uvi))
            light_Data1 = float(uvs)
            light_Data2 = float(round(uvi,2))
    time.sleep(0.5)

if buf210 == False:
    print("ENS210 initialize error.")
    while True:
        pass
else:
    print("ENS210 initialize register finished.")
ens210.ENS210_SetSingleMode(False)

'''
if buf160 == False:
    print("ENS160 initialize error.")
    while buf160== False:
        pass
else:
    print("ENS160 initialize register finished.")
'''

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

'''
try:
    while True:
        printTime()
        printData1()
        printData2()
        printData3()

except KeyboardInterrupt:
    pass
'''

GPIO.cleanup()
