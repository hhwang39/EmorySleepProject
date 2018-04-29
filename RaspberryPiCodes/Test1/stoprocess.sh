#!/bin/bash
GPIODIR=/sys/class/gpio
function initLED(){
 if [ ! -f $GPIODIR/gpio24 ];then
  echo 24 > $GPIODIR/export
  echo out > $GPIODIR/gpio24/direction
  echo 22 > $GPIODIR/export
  echo out > $GPIODIR/gpio22/direction
  echo 23 > $GPIODIR/export
  echo out > $GPIODIR/gpio23/direction
 fi
}
function offLED(){
 echo 0 > $GPIODIR/gpio22/value 
 echo 0 > $GPIODIR/gpio23/value 
 echo 0 > $GPIODIR/gpio24/value 
}
function greenLEDon(){
  echo 1 > $GPIODIR/gpio22/value
}
function blueLEDon(){
  echo 1 > $GPIODIR/gpio24/value
}
function redLEDon(){
  echo 1 > $GPIODIR/gpio23/value
}
PROJECTHOME=/home/pi/mbientlab/Project/Test1
cd $PROJECTHOME
process=`ps -efa|grep python|grep -v grep|awk '{print $3, $2}'`
kill -9 `echo $process` 
offLED
