#!/usr/bin/env python3

# RTrobot LTR390UV Test
# http://rtrobot.org


import time
import fcntl
import array
import RPi.GPIO as GPIO

I2C_SLAVE = 0x0703
SPI_BUS = 0
SPI_DEVICE = 0


class RTrobot_LTR390UV:

    # Addresses of the LTR390UV registers
    LTR390UV_REG_MAIN_CTRL = (0x00)
    LTR390UV_REG_ALS_UVS_MEAS_RATE = (0x04)
    LTR390UV_REG_ALS_UVS_GAIN = (0x05)
    LTR390UV_REG_PART_ID = (0x06)
    LTR390UV_REG_MAIN_STATUS = (0x07)
    LTR390UV_REG_ALS_DATA_0 = (0x0d)
    LTR390UV_REG_ALS_DATA_1 = (0x0e)
    LTR390UV_REG_ALS_DATA_2 = (0x0f)
    LTR390UV_REG_UVS_DATA_0 = (0x10)
    LTR390UV_REG_UVS_DATA_1 = (0x11)
    LTR390UV_REG_UVS_DATA_2 = (0x12)
    LTR390UV_REG_INT_CFG = (0x19)
    LTR390UV_REG_INT_PST = (0x1a)
    LTR390UV_REG_ALS_UVS_THRES_UP_0 = (0x21)
    LTR390UV_REG_ALS_UVS_THRES_UP_1 = (0x22)
    LTR390UV_REG_ALS_UVS_THRES_UP_2 = (0x23)
    LTR390UV_REG_ALS_UVS_THRES_LOW_0 = (0x24)
    LTR390UV_REG_ALS_UVS_THRES_LOW_1 = (0x25)
    LTR390UV_REG_ALS_UVS_THRES_LOW_2 = (0x26)

    # LTR-390 MAIN_CTRL
    LTR390UV_LOWPOWER_ENABLE = (0xfd)
    LTR390UV_LOWPOWER_DISABLE = (0x02)
    LTR390UV_MODE_ALS = (0xf7)
    LTR390UV_MODE_UVS = (0x08)

    # LTR-390 ALS/UVS measurement gain range
    LTR390UV_GAIN_RANGE_1 = (0x00)
    LTR390UV_GAIN_RANGE_3 = (0x01)
    LTR390UV_GAIN_RANGE_6 = (0x02)
    LTR390UV_GAIN_RANGE_9 = (0x03)
    LTR390UV_GAIN_RANGE_18 = (0x04)

    # LTR-390 ALS/UVS  resolution
    LTR390UV_RESOLUTION_20BIT = (0x00)
    LTR390UV_RESOLUTION_19BIT = (0x10)
    LTR390UV_RESOLUTION_18BIT = (0x20)
    LTR390UV_RESOLUTION_17BIT = (0x30)
    LTR390UV_RESOLUTION_16BIT = (0x40)
    LTR390UV_RESOLUTION_13BIT = (0x50)

    # LTR-390 ALS/UVS measurement
    LTR390UV_MEASUREMENT_RATE_25MS = (0x00)
    LTR390UV_MEASUREMENT_RATE_50MS = (0x01)
    LTR390UV_MEASUREMENT_RATE_100MS = (0x02)
    LTR390UV_MEASUREMENT_RATE_200MS = (0x03)
    LTR390UV_MEASUREMENT_RATE_500MS = (0x04)
    LTR390UV_MEASUREMENT_RATE_1000MS = (0x05)
    LTR390UV_MEASUREMENT_RATE_2000MS = (0x06)

    # LTR-390 Interrupt Trigger Threshold Count
    LTR390UV_PST_EVERY = (0x00)
    LTR390UV_PST_CONSECUTIVE_2 = (0x10)
    LTR390UV_PST_CONSECUTIVE_3 = (0x20)
    LTR390UV_PST_CONSECUTIVE_4 = (0x30)
    LTR390UV_PST_CONSECUTIVE_5 = (0x40)
    LTR390UV_PST_CONSECUTIVE_6 = (0x50)
    LTR390UV_PST_CONSECUTIVE_7 = (0x60)
    LTR390UV_PST_CONSECUTIVE_8 = (0x70)
    LTR390UV_PST_CONSECUTIVE_9 = (0x80)
    LTR390UV_PST_CONSECUTIVE_10 = (0x90)
    LTR390UV_PST_CONSECUTIVE_11 = (0xa0)
    LTR390UV_PST_CONSECUTIVE_12 = (0xb0)
    LTR390UV_PST_CONSECUTIVE_13 = (0xc0)
    LTR390UV_PST_CONSECUTIVE_14 = (0xd0)
    LTR390UV_PST_CONSECUTIVE_15 = (0xe0)
    LTR390UV_PST_CONSECUTIVE_16 = (0xf0)

    # LTR-390 Interrupt mode
    LTR390UV_INT_ALS = (0x10)
    LTR390UV_INT_UVS = (0x30)

    LTR390UV_ADDRESS = (0x53)

    def __init__(self, i2c_no=3, i2c_addr=LTR390UV_ADDRESS, spi_cs=8):
        global LTR390UV_rb, LTR390UV_wb
        LTR390UV_rb = open("/dev/i2c-"+str(i2c_no), "rb", buffering=0)
        LTR390UV_wb = open("/dev/i2c-"+str(i2c_no), "wb", buffering=0)
        fcntl.ioctl(LTR390UV_rb, I2C_SLAVE, i2c_addr)
        fcntl.ioctl(LTR390UV_wb, I2C_SLAVE, i2c_addr)

    # LTR390UV Initialization
    def LTR390UV_Init(self):
        # Read ID
        cmd = [self.LTR390UV_REG_PART_ID]
        id = self.LTR390UV_i2c_read(cmd, 1)
        if (id[0] & 0xf0) != 0xb0:
            return False
        self.LTR390UV_LowPower(False)
        return True

    # LTR390UV  set low power mode
    def LTR390UV_LowPower(self, enable):
        buf = [self.LTR390UV_REG_MAIN_CTRL, 0x00]
        cmd = [self.LTR390UV_REG_MAIN_CTRL]
        tmp = self.LTR390UV_i2c_read(cmd, 1)
        if enable == True:
            buf[1] = self.LTR390UV_LOWPOWER_ENABLE & tmp[0]
        else:
            buf[1] = self.LTR390UV_LOWPOWER_DISABLE | tmp[0]
        self.LTR390UV_i2c_write(buf)
        tmp = self.LTR390UV_i2c_read(cmd, 1)

    # LTR390UV  set mode
    def LTR390UV_SetMode(self, mode):
        buf = [self.LTR390UV_REG_MAIN_CTRL, 0x00]
        cmd = [self.LTR390UV_REG_MAIN_CTRL]
        tmp = self.LTR390UV_i2c_read(cmd, 1)
        if mode == self.LTR390UV_MODE_ALS:
            buf[1] = self.LTR390UV_MODE_ALS & tmp[0]
        else:
            buf[1] = self.LTR390UV_MODE_UVS | tmp[0]
        self.LTR390UV_i2c_write(buf)

    # LTR390UV  get mode
    def LTR390UV_GetMode(self):
        cmd = [self.LTR390UV_REG_MAIN_CTRL]
        buf = self.LTR390UV_i2c_read(cmd, 1)
        if buf[0] >> 3 == 0x01:
            return self.LTR390UV_MODE_UVS
        else:
            return self.LTR390UV_MODE_ALS

    # LTR390UV  set the sensor gain
    def LTR390UV_SetGain(self, mode):
        buf = [self.LTR390UV_REG_ALS_UVS_GAIN, mode]
        self.LTR390UV_i2c_write(buf)

    # LTR390UV  get the sensor gain
    def LTR390UV_GetGain(self):
        cmd = [self.LTR390UV_REG_ALS_UVS_GAIN]
        buf = self.LTR390UV_i2c_read(cmd, 1)
        return buf[0] & 0x07

    # this register controls als/uvs measurement resolution,
    # gain setting and measurement rate.
    # when the measurement  rate is programmed to be faster than possible for the
    # programmed adc measurement ,the rate will be lowered than programmed.
    def LTR390UV_SetMeasurement(self,mode):
        buf = [self.LTR390UV_REG_ALS_UVS_MEAS_RATE, mode]
        self.LTR390UV_i2c_write(buf)

    #Set the upper and lower interrupt limits
    #range: 0 - 1048575
    def LTR390UV_SetThresholds(self, low,  up):
        lower = [0x00,0x00,0x00]
        upper = [0x00,0x00,0x00]
        lower[0] = low & 0xff
        lower[1] = (low & 0xff00) >> 8
        lower[2] = (low & 0xf0000) >> 12
        buf=[self.LTR390UV_REG_ALS_UVS_THRES_LOW_0,lower[0],lower[1],lower[2]]
        self.LTR390UV_i2c_write(buf)
        upper[0] = up & 0xff
        upper[1] = (up & 0xff00) >> 8
        upper[2] = (up & 0xf0000) >> 12
        buf=[self.LTR390UV_REG_ALS_UVS_THRES_UP_0,upper[0],upper[1],upper[2]]
        self.LTR390UV_i2c_write(buf)

    #Set the interrupt type and interrupt trigger threshold count
    def LTR390UV_SetInterrupt(self, enable, mode, count):
        buf = [self.LTR390UV_REG_INT_CFG,0x00]
        if enable == True:
            buf[1] = mode | 0x04
            self.LTR390UV_i2c_write(buf)
            buf = [self.LTR390UV_REG_INT_PST,count]
            self.LTR390UV_i2c_write(buf)
        else:
            self.LTR390UV_i2c_write(buf)

    # LTR390UV  get the Resolution
    def LTR390UV_GetResolution(self):
        cmd = [self.LTR390UV_REG_ALS_UVS_MEAS_RATE]
        buf = self.LTR390UV_i2c_read(cmd, 1)
        buf[0] &= 0x70;
        buf[0] = 7 & (buf[0] >> 4);
        return buf[0]

    # LTR390UV  Get Data Statut
    def LTR390UV_GetDataStatus(self):
        cmd = [self.LTR390UV_REG_MAIN_STATUS]
        buf = self.LTR390UV_i2c_read(cmd, 1)
        if (buf[0] & 0x08) >> 3 == 0x01:
            return True
        else:
            return False

    # LTR390UV  Get als value
    def LTR390UV_GetALS(self):
        cmd = [self.LTR390UV_REG_ALS_DATA_0]
        buf = self.LTR390UV_i2c_read(cmd, 3)
        return buf[2] * 65536 + buf[1] * 256 + buf[0]

    # WFAC was window factor. 1 as no window or clear window glass, >1 as tinted windows glass 
    # unit lux.
    def LTR390UV_GetLUX(self,als,WFAC):
        gain_buf = [1.0, 3.0, 6.0, 9.0, 18.0]
        res_buf = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
        gain = self.LTR390UV_GetGain()
        res = self.LTR390UV_GetResolution()
        return 0.6 * (als) / (gain_buf[gain] * res_buf[res]) * WFAC

    # LTR390UV  Get UV value
    def LTR390UV_GetUVS(self):
        cmd = [self.LTR390UV_REG_UVS_DATA_0]
        buf = self.LTR390UV_i2c_read(cmd, 3)
        return buf[2] * 65536 + buf[1] * 256 + buf[0]

    # WFAC was window factor. 1 as no window or clear window glass, >1 as tinted windows glass
    # unit uw/cm2.
    def LTR390UV_GetUVI(self,uvs,WFAC):
        gain_buf = [1.0, 3.0, 6.0, 9.0, 18.0]
        res_buf = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
        gain = self.LTR390UV_GetGain()
        res = self.LTR390UV_GetResolution()
        return (uvs) / ((gain_buf[gain] / 18) * (res_buf[res] / 4) * 2300.0) * WFAC

    ######################################i2C######################################
    def LTR390UV_i2c_read(self, reg, len=1):
        self.LTR390UV_i2c_write(reg)
        tmp = LTR390UV_rb.read(len)
        return array.array('B', tmp)

    def LTR390UV_i2c_write(self, reg):
        buf_binary = bytearray(reg)
        LTR390UV_wb.write(buf_binary)
