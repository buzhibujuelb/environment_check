import time
import RPi.GPIO as GPIO



def alert():

	alert_fm = 13 # 设置引脚
	alert_time = 1 # 设置发出警报的时间
	alert_Hz = 4978	# 声音频率

	GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)
	GPIO.setup(alert_fm, GPIO.OUT) # 设置 GPIO 13 为输出
	pwm = GPIO.PWM(alert_fm, alert_Hz) # 设置 GPIO 13 为 PWM 输出, 设置脉冲

	pwm.start(0)	# 初始化占空比为 0%
	pwm.ChangeDutyCycle(50) 	# 改变占空比为 50%
	time.sleep(alert_time) 	# 开始发声
	
	
	pwm.stop()
	GPIO.cleanup()


if __name__ == '__main__':
	alert()