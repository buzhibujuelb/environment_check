#coding:utf-8
import time

# 导入UI模块
# 导入GPIO控制薄块
import RPi.GPIO as GPIO
# 定时器模块
import threading

# 主页面设置
print('欢迎使用双色LED灯控制器')

# 定义引脚
pins = {0:16,1:18}
# 设置使用的引脚编码模式
GPIO.setmode(GPIO.BOARD)
# 设置隐藏警告
GPIO.setwarnings(False)
# 初始化物理引脚 13 和 15
GPIO.setup(pins[0],GPIO.OUT)
GPIO.setup(pins[1],GPIO.OUT)

# 定义全局字段 用来处理闪烁功能
# f:是否闪烁  l:下次点亮红灯或绿灯
f = False
l = False

# 控制红灯亮
def redClick():
    global f
    f = False
    GPIO.output(pins[0],GPIO.HIGH)
    GPIO.output(pins[1],GPIO.LOW)
	
# 控制绿灯亮
def greenClick():
    global f
    f = False
    GPIO.output(pins[0],GPIO.LOW)
    GPIO.output(pins[1],GPIO.HIGH)

# 退出程序
def stopClick():
    global f
    f = False
    GPIO.output(pins[0],GPIO.LOW)
    GPIO.output(pins[1],GPIO.LOW)
    GPIO.cleanup()
    exit()

# 循环闪烁
def loop():
    global f
    global timer
    global l
    if f == False:
        return
    if l:
        GPIO.output(pins[0],GPIO.HIGH)
        GPIO.output(pins[1],GPIO.LOW)
    else:
        GPIO.output(pins[0],GPIO.LOW)
        GPIO.output(pins[1],GPIO.HIGH)
    # 转换下次闪烁的颜色
    l = not l

# 定义全局定时器

# 开始进行闪烁
def flckerClick():
    global f
    global timer
    f = True
    for i in range(10):
        loop()
        time.sleep(0.1)
# UI上的按钮布局
print("红灯停")
redClick()
time.sleep(1)

print("绿灯行")
greenClick()
time.sleep(1)

print("闪烁请注意")
flckerClick()
time.sleep(1)

print("关闭")
stopClick()
# 进入消息循环
