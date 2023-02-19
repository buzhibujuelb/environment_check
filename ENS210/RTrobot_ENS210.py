#!/usr/bin/env python3

# RTrobot ENS210 Test
# http://rtrobot.org
# SPI use spi0

from ast import While
from operator import le, mod
from os import lseek
import time
import fcntl
import array
import spidev
import RPi.GPIO as GPIO
import math

I2C_SLAVE = 0x0703
SPI_BUS = 0
SPI_DEVICE = 0


class RTrobot_ENS210:

    ENS210_ADDRESS = (0x43)
    ENS210_REG_PART_ID = (0x00)
    ENS210_REG_UID = (0x04)
    ENS210_REG_SYS_CTRL = (0x10)
    ENS210_REG_SYS_STAT = (0x11)
    ENS210_REG_SENS_RUN = (0x21)
    ENS210_REG_SENS_START = (0x22)
    ENS210_REG_SENS_STOP = (0x23)
    ENS210_REG_SENS_STAT = (0x24)
    ENS210_REG_T_VAL = (0x30)
    ENS210_REG_H_VAL = (0x33)
    Celsius = (0x00)
    Fahrenheit = (0x01)
    Kelvin = (0x02)
    Relative = (0x00)
    Absolute = (0x01)

    # Conversion time in ms for single shot T/H measurement
    ENS210_THCONV_SINGLE_MS = (130)
    # Conversion time in ms for continuous T/H measurement
    ENS210_THCONV_CONT_MS = (238)

    def __init__(self, i2c_no=1, i2c_addr=ENS210_ADDRESS):
        global ENS210_rb, ENS210_wb
        ENS210_rb = open("/dev/i2c-"+str(i2c_no), "rb", buffering=0)
        ENS210_wb = open("/dev/i2c-"+str(i2c_no), "wb", buffering=0)
        fcntl.ioctl(ENS210_rb, I2C_SLAVE, i2c_addr)
        fcntl.ioctl(ENS210_wb, I2C_SLAVE, i2c_addr)
        self.ENS210_SingleMode = False

    # ENS210 Initialization
    def ENS210_Init(self):
        self.ENS210_LowPower(False)
        # Read ID
        cmd = [self.ENS210_REG_PART_ID]
        id = self.ENS210_i2c_read(cmd, 2)
        if id[0] != 0x10 and id[1] != 0x02:
            return False
        return True

    # Sets ENS210 to low (true) or high (false) power.
    def ENS210_LowPower(self, status):
        buf = [self.ENS210_REG_SYS_CTRL, 0x00]
        if status == True:
            buf[1] = 0x01
        self.ENS210_i2c_write(buf)

    # Reads measurement data from the ENS210. Returns false on I2C problems.
    def ENS210_ReadValue(self):
        cmd = [self.ENS210_REG_T_VAL]
        rev_data = self.ENS210_i2c_read(cmd, len=6)
        t_val = rev_data[2] << 16 | rev_data[1] << 8 | rev_data[0]
        h_val = rev_data[5] << 16 | rev_data[4] << 8 | rev_data[3]
        return t_val, h_val

    # Performs one single shot temperature and relative humidity measurement.
    def ENS210_GetMeasure(self):
        if self.ENS210_SingleMode == True:
            cmd = [self.ENS210_REG_SENS_RUN, 0x00]
            self.ENS210_i2c_write(cmd)
        buf = [self.ENS210_REG_SENS_START, 0x03]
        self.ENS210_i2c_write(buf)
        if self.ENS210_SingleMode == True:
            time.sleep(self.ENS210_THCONV_SINGLE_MS/1000)
        else:
            time.sleep(self.ENS210_THCONV_CONT_MS/1000)
        return self.ENS210_ReadValue()

    # Configures ENS210 measurement mode
    # false for continuous mode / true for  single shot measurement. Returns false on I2C problems.
    def ENS210_SetSingleMode(self, status):
        buf = [self.ENS210_REG_SENS_RUN, 0x03]
        if status == True:
            buf[1] = 0x00
            self.ENS210_SingleMode = True
        else:
            self.ENS210_SingleMode = False
        self.ENS210_i2c_write(buf)

    def ENS210_Convert_Temperature(self, value, mode=Celsius):
        t = (value & 0xFFFF)/1.0
        if mode == self.Celsius:
            return t / 64 - 27315 / 100
        if mode == self.Kelvin:
            return t / 64
        if mode == self.Fahrenheit:
            return t * 9 / 320 - 45967 / 100
        return 0

    def ENS210_Convert_Humidity(self, value):
        h = (value & 0xFFFF)/1.0
        return h / 512

    def ENS210_ConverAbsoluteHumidityPercent(self, t_value, h_value):
        # taken from https://carnotcycle.wordpress.com/2012/08/04/how-to-convert-relative-humidity-to-absolute-humidity/
        # precision is about 0.1°C in range -30 to 35°C
        # August-Roche-Magnus   6.1094 exp(17.625 x T)/(T + 243.04)
        # Buck (1981)     6.1121 exp(17.502 x T)/(T + 240.97)
        # reference https://www.eas.ualberta.ca/jdwilson/EAS372_13/Vomel_CIRES_satvpformulae.html    // Use Buck (1981)
        return (6.1121 * math.pow(2.718281828, (17.67 * self.ENS210_Convert_Temperature(t_value)) / (self.ENS210_Convert_Temperature(t_value) + 243.5)) * self.ENS210_Convert_Humidity(h_value) * 18.01534) / ((273.15 + self.ENS210_Convert_Temperature(t_value)) * 8.21447215)

    ######################################i2C######################################
    def ENS210_i2c_read(self, reg, len=1):
        self.ENS210_i2c_write(reg)
        tmp = ENS210_rb.read(len)
        return array.array('B', tmp)

    def ENS210_i2c_write(self, reg):
        buf_binary = bytearray(reg)
        ENS210_wb.write(buf_binary)
