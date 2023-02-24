#!/usr/bin/env python3

# RTrobot ENS160 Test
# http://rtrobot.org
# SPI use spi0

from ast import While
from distutils.command.install_egg_info import safe_name
import time
import fcntl
import array
import spidev
import RPi.GPIO as GPIO
import math

I2C_SLAVE = 0x0703
SPI_BUS = 0
SPI_DEVICE = 0


class RTrobot_ENS160:

    # ENS160 data register fields
    ENS160_COMMAND_NOP = 0x00
    ENS160_COMMAND_CLRGPR = 0xCC
    ENS160_COMMAND_GET_APPVER = 0x0E
    ENS160_COMMAND_SETTH = 0x02
    ENS160_COMMAND_SETSEQ = 0xC2

    ENS160_OPMODE_RESET = 0xF0
    ENS160_OPMODE_DEP_SLEEP = 0x00
    ENS160_OPMODE_IDLE = 0x01
    ENS160_OPMODE_STD = 0x02
# <--not find in database
    ENS160_OPMODE_CUSTOM = 0xC0
    ENS160_OPMODE_D0 = 0xD0
    ENS160_OPMODE_D1 = 0xD1
    ENS160_OPMODE_BOOTLOADER = 0xB0
# <--not find in database

    ENS160_INT_PIN_LOW = 0x00
    ENS160_INT_PIN_HIGH = 0x40
    ENS160_INT_PIN_OPENDRAIN = 0x00
    ENS160_INT_PIN_PUSH = 0x10

    ENS160_SEQ_ACK_NOTCOMPLETE = 0x80
    ENS160_SEQ_ACK_COMPLETE = 0xC0

    ENS160_REG_PART_ID = 0x00
    ENS160_REG_OPMODE = 0x10
    ENS160_REG_CONFIG = 0x11
    ENS160_REG_COMMAND = 0x12
    ENS160_REG_TEMP_IN = 0x13
    ENS160_REG_RH_IN = 0x15
    ENS160_REG_DATA_STATUS = 0x20
    ENS160_REG_DATA_AQI = 0x21
    ENS160_REG_DATA_TVOC = 0x22
    ENS160_REG_DATA_ECO2 = 0x24
    ENS160_REG_DATA_BL = 0x28
    ENS160_REG_DATA_T = 0x30
    ENS160_REG_DATA_RH = 0x32
    ENS160_REG_DATA_MISR = 0x38
    ENS160_REG_GPR_WRITE_0 = 0x40
    ENS160_REG_GPR_WRITE_1 = ENS160_REG_GPR_WRITE_0 + 1
    ENS160_REG_GPR_WRITE_2 = ENS160_REG_GPR_WRITE_0 + 2
    ENS160_REG_GPR_WRITE_3 = ENS160_REG_GPR_WRITE_0 + 3
    ENS160_REG_GPR_WRITE_4 = ENS160_REG_GPR_WRITE_0 + 4
    ENS160_REG_GPR_WRITE_5 = ENS160_REG_GPR_WRITE_0 + 5
    ENS160_REG_GPR_WRITE_6 = ENS160_REG_GPR_WRITE_0 + 6
    ENS160_REG_GPR_WRITE_7 = ENS160_REG_GPR_WRITE_0 + 7
    ENS160_REG_GPR_READ_0 = 0x48
    ENS160_REG_GPR_READ_4 = ENS160_REG_GPR_READ_0 + 4
    ENS160_REG_GPR_READ_6 = ENS160_REG_GPR_READ_0 + 6
    ENS160_REG_GPR_READ_7 = ENS160_REG_GPR_READ_0 + 7

    ENS160_DATA_STATUS_NEWDAT = 0x02
    ENS160_DATA_STATUS_NEWGPR = 0x01

    ENS160_MODE_I2C = (1)
    ENS160_MODE_SPI = (2)
    ENS160_MODE = (0)
    ENS160_CSPIN = (0)
    ENS160_ADDRESS = (0x53)

    _data_aqi = 0
    _data_tvoc = 0
    _data_eco2 = 0
    _step_counts = 0
    _hp0_rs = 0
    _hp0_bl = 0
    _hp1_rs = 0
    _hp1_bl = 0
    _hp2_rs = 0
    _hp2_bl = 0
    _hp3_rs = 0
    _hp3_bl = 0
    _misr = 0

    def __init__(self, mode=ENS160_MODE_I2C, i2c_no=1, i2c_addr=ENS160_ADDRESS, spi_cs=8):
        self.ENS160_MODE = mode
        if self.ENS160_MODE == self.ENS160_MODE_I2C:
            global ENS160_rb, ENS160_wb
            ENS160_rb = open("/dev/i2c-"+str(i2c_no), "rb", buffering=0)
            ENS160_wb = open("/dev/i2c-"+str(i2c_no), "wb", buffering=0)
            fcntl.ioctl(ENS160_rb, I2C_SLAVE, i2c_addr)
            fcntl.ioctl(ENS160_wb, I2C_SLAVE, i2c_addr)
        if self.ENS160_MODE == self.ENS160_MODE_SPI:
            self.ENS160_CSPIN = spi_cs
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.ENS160_CSPIN, GPIO.OUT)
            GPIO.output(self.ENS160_CSPIN, True)
            global spi
            spi = spidev.SpiDev()
            spi.open(SPI_BUS, SPI_DEVICE)
            spi.no_cs=True
            spi.max_speed_hz = 2000000

    # ENS160 Initialization
    def ENS160_Init(self):
        # Read ID
        cmd = [self.ENS160_REG_PART_ID]
        id = self.ENS160_read(cmd, 2)
        if id[0] != 0x60 and id[1] != 0x01:
            return False
        # reboot and reset register
        self.ENS160_Reset()

        # Initialize idle mode and confirms
        self.ENS160_SetMode(self.ENS160_OPMODE_IDLE)
        time.sleep(0.01)
        self.ENS160_GetFirmware()
        self.ENS160_ClearCommand()
        time.sleep(0.01)
        # configuration mode
        self.ENS160_SetMode(self.ENS160_OPMODE_STD)
        time.sleep(0.05)
        # Disable Interrupt pin
        self.ENS160_SetInterrupt(
            False, self.ENS160_INT_PIN_LOW, self.ENS160_INT_PIN_OPENDRAIN)
        return True

    # Initialize definition of custom mode with <n> steps
    def ENS160_InitCustomMode(self):
        cmd = [self.ENS160_REG_COMMAND, self.ENS160_COMMAND_SETSEQ]
        self.ENS160_SetMode(self.ENS160_OPMODE_IDLE)
        self.ENS160_ClearCommand()
        self.ENS160_write()
        time.sleep(0.01)

    # Add a step to custom measurement profile with definition of duration, enabled data acquisition and temperature for each hotplate
    def ENS160_AddCustomStep(self, time, measureHP0, measureHP1, measureHP2, measureHP3, tempHP0, tempHP1, tempHP2, tempHP3):
        cmd = [self.ENS160_REG_GPR_WRITE_0, 0x00]
        cmd[1] = (((time / 24) - 1) << 6) & 0xFF
        if measureHP0:
            cmd[1] = cmd[1] | 0x20
        if measureHP1:
            cmd[1] = cmd[1] | 0x10
        if measureHP2:
            cmd[1] = cmd[1] | 0x8
        if measureHP3:
            cmd[1] = cmd[1] | 0x4
        self.ENS160_write(cmd)

        cmd[0] = self.ENS160_REG_GPR_WRITE_1
        cmd[1] = (((time / 24) - 1) >> 2)
        self.ENS160_write(cmd)
        cmd[0] = self.ENS160_REG_GPR_WRITE_2
        cmd[1] = (tempHP0 / 2)
        self.ENS160_write(cmd)
        cmd[0] = self.ENS160_REG_GPR_WRITE_3
        cmd[1] = (tempHP1 / 2)
        self.ENS160_write(cmd)
        cmd[0] = self.ENS160_REG_GPR_WRITE_4
        cmd[1] = (tempHP2 / 2)
        self.ENS160_write(cmd)
        cmd[0] = self.ENS160_REG_GPR_WRITE_5
        cmd[1] = (tempHP3 / 2)
        self.ENS160_write(cmd)
        cmd[0] = self.ENS160_REG_GPR_WRITE_6
        cmd[1] = self._step_counts - 1
        self.ENS160_write(cmd)

        if self._step_counts == 1:
            cmd[0] = self.ENS160_REG_GPR_WRITE_7
            cmd[1] = 128
            self.ENS160_write(cmd)
        else:
            cmd[0] = self.ENS160_REG_GPR_WRITE_7
            cmd[1] = 0
            self.ENS160_write(cmd)
        time.sleep(0.01)
        cmd2 = [self.ENS160_REG_GPR_READ_7]
        seq_ack = self.ENS160_read(cmd2)
        time.sleep(0.01)
        if (self._step_counts | self.ENS160_SEQ_ACK_COMPLETE) != seq_ack:
            self._step_counts = self._step_counts-1

    # ENS160 Get Temperature Value
    def ENS160_Get_Temperature(self):
        buf = [self.ENS160_OUT_TEMP_L]
        data = self.ENS160_read(buf, 2)
        temp = (data[1] << 8 | data[0])/256.0+25.0
        return temp

    # ENS160 Set Temperature and humidity
    #    eg: ENS160_SetTempHum(25,50)
    def ENS160_SetTempHum(self, temperature, humidity):
        cmd = [self.ENS160_REG_TEMP_IN, 0x00, 0x00, 0x00, 0x00]
        ah_scaled = int((temperature + 273.15) * 64)
        cmd[1] = ah_scaled & 0xff
        cmd[2] = (ah_scaled & 0xFF00) >> 8
        ah_scaled = int(humidity * 512)
        cmd[3] = ah_scaled & 0xFF
        cmd[4] = (ah_scaled & 0xFF00) >> 8
        self.ENS160_write(cmd)

    # Perfrom measurement and stores result in internal variables
    def ENS160_measure(self, waitForNew, temperature, humidity):
        status = 0x00
        newData = False
        if waitForNew == True:
            while (0x03 and status) == 0:
                cmd = [self.ENS160_REG_DATA_STATUS]
                data = self.ENS160_read(cmd)
                status = data[0]
        else:
            cmd = [self.ENS160_REG_DATA_STATUS]
            data = self.ENS160_read(cmd)
            status = data[0]
        self.ENS160_SetTempHum(temperature, humidity)
        # Read predictions
        if 0x02 == (0x02 & status):
            newData = True
            cmd = [self.ENS160_REG_DATA_AQI]
            i2cbuf = self.ENS160_read(cmd, 5)
            self._data_tvoc = i2cbuf[1] | (i2cbuf[2] << 8)
            self._data_eco2 = i2cbuf[3] | (i2cbuf[4] << 8)
            self._data_aqi = i2cbuf[0]
        # Read raw resistance values
        if 0x01 == (0x01 & status):
            newData = True
            cmd = [self.ENS160_REG_GPR_READ_0]
            i2cbuf = self.ENS160_read(cmd, 8)
            self._hp0_rs = math.pow(2, (i2cbuf[0] | (i2cbuf[1] << 8))/2048)
            self._hp1_rs = math.pow(2, (i2cbuf[2] | (i2cbuf[3] << 8))/2048)
            self._hp2_rs = math.pow(2, (i2cbuf[4] | (i2cbuf[5] << 8))/2048)
            self._hp3_rs = math.pow(2, (i2cbuf[6] | (i2cbuf[7] << 8))/2048)
        if (0x02 == (0x02 & status)) or (0x01 == (0x01 & status)):
            newData = True
            cmd = [self.ENS160_REG_DATA_BL]
            i2cbuf = self.ENS160_read(cmd, 8)
            self._hp0_bl = math.pow(2, (i2cbuf[0] | (i2cbuf[1] << 8))/2048)
            self._hp1_bl = math.pow(2, (i2cbuf[2] | (i2cbuf[3] << 8))/2048)
            self._hp2_bl = math.pow(2, (i2cbuf[4] | (i2cbuf[5] << 8))/2048)
            self._hp3_bl = math.pow(2, (i2cbuf[6] | (i2cbuf[7] << 8))/2048)
            cmd[0] = self.ENS160_REG_DATA_MISR
            i2cbuf2 = self.ENS160_read(cmd, 1)
            self._misr = i2cbuf2[0]
        return newData

    # EENS160 Set Interrupt
    def ENS160_SetInterrupt(self, mode, level, status):
        cmd = [self.ENS160_REG_CONFIG, 0x00]
        if mode == True:
            cmd[1] = level | status | 0x01
        self.ENS160_write(cmd)

    # ENS160 Clear All Register
    def ENS160_ClearCommand(self):
        cmd = [self.ENS160_REG_COMMAND, self.ENS160_COMMAND_NOP]
        self.ENS160_write(cmd)
        cmd[1] = self.ENS160_COMMAND_CLRGPR
        self.ENS160_write(cmd)
        time.sleep(0.01)
        cmd2 = [self.ENS160_REG_DATA_STATUS]
        self.ENS160_read(cmd2)
        time.sleep(0.01)

    # ENS160 Get Firmware Version
    def ENS160_GetFirmware(self):
        buf = [self.ENS160_REG_COMMAND, self.ENS160_COMMAND_GET_APPVER]
        self.ENS160_write(buf)
        time.sleep(0.01)
        cmd = [self.ENS160_REG_GPR_READ_4]
        id = self.ENS160_read(cmd, 3)
        print("Firware:%d.%d.%d" % (id[0], id[1], id[2]))

    # ENS160 Set Mode
    def ENS160_SetMode(self, mode):
        buf = [self.ENS160_REG_OPMODE, mode]
        self.ENS160_write(buf)

    # ENS160 reboot
    def ENS160_Reset(self):
        buf = [self.ENS160_REG_OPMODE, self.ENS160_OPMODE_RESET]
        self.ENS160_write(buf)
        time.sleep(0.01)

    ############################################################################
    def ENS160_read(self, reg, len=1):
        if self.ENS160_MODE == self.ENS160_MODE_I2C:
            buf = self.ENS160_i2c_read(reg, len)
        if self.ENS160_MODE == self.ENS160_MODE_SPI:
            reg[0]=(reg[0] << 1) | 0x01
            buf = self.ENS160_spi_read(reg, len)
        return buf

    def ENS160_write(self, reg):
        if self.ENS160_MODE == self.ENS160_MODE_I2C:
            self.ENS160_i2c_write(reg)
        if self.ENS160_MODE == self.ENS160_MODE_SPI:
            reg[0]=(reg[0] << 1) & 0xFE
            self.ENS160_spi_write(reg)

    ######################################i2C######################################

    def ENS160_i2c_read(self, reg, len=1):
        self.ENS160_i2c_write(reg)
        tmp = ENS160_rb.read(len)
        return array.array('B', tmp)

    def ENS160_i2c_write(self, reg):
        buf_binary = bytearray(reg)
        ENS160_wb.write(buf_binary)

    ######################################SPI######################################
    def ENS160_spi_read(self, reg, len=1):
        GPIO.output(self.ENS160_CSPIN, False)
        spi.writebytes(reg)
        data = spi.readbytes(len)
        GPIO.output(self.ENS160_CSPIN, True)
        return data

    def ENS160_spi_write(self, reg):
        GPIO.output(self.ENS160_CSPIN, False)
        time.sleep(0.001)
        buf_binary = bytearray(reg)
        spi.writebytes(buf_binary)
        time.sleep(0.001)
        GPIO.output(self.ENS160_CSPIN, True)
