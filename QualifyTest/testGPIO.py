import RPi.GPIO as GPIO
from time import sleep
GPIO.setmode(GPIO.BCM)
mode = GPIO.getmode()
print "mode %s"%mode
GPIO.setwarnings(False)
channel=23
redLED=23
greenLED=22
blueLED=24
channels=[redLED, greenLED, blueLED]
GPIO.setup(channels, GPIO.OUT)
sleep(1.0)
print "red"
GPIO.output(redLED, GPIO.HIGH)
sleep(5.0)
GPIO.output(redLED, GPIO.LOW)
sleep(1.0)
print "blue"
GPIO.output(blueLED, GPIO.HIGH)
sleep(5.0)
GPIO.output(blueLED, GPIO.LOW)
sleep(1.0)
print "green"
GPIO.output(greenLED, GPIO.HIGH)
sleep(5.0)
GPIO.output(greenLED, GPIO.LOW)
