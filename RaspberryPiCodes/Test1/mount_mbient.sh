#!/bin/bash
GPIODIR=/sys/class/gpio
function initLED(){
 if [ ! -f "$GPIODIR/gpio24" ];then
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
blueLEDon
if [ ! -f "/media/pi/EMORYSLP/data/deviceaddress.txt" ];then
dummy=1
else
 cp /media/pi/EMORYSLP/data/deviceaddress.txt /home/pi/mbientlab/Project/Test1
 cp /media/pi/EMORYSLP/data/deviceaddress.txt /home/pi/mbientlab/Project/calibration
 sleep 2
 rm /media/pi/EMORYSLP/data/deviceaddress.txt
fi
if [ ! -f "/media/pi/EMORYSLP/data/calibration.txt" ];then

if [ ! -f "/home/pi/mbientlab/Project/Test1/data1.db" ];then
   sleep 2
   umount /media/pi/EMORYSLP 
   offLED

else
   STARTUPFILE=startdate.txt
   rm $STARTUPFILE
   sqlite3 -header -csv data1.db "select * from acc;" > data1.csv
   resultcsv=$?
   cd /home/pi/mbientlab/Project/Test1
   mkdir backup
   cp data1.db /home/pi/mbientlab/Project/Test1/backup
   mv data1.db /media/pi/EMORYSLP/data
   resultdb=$?
   mv data1.*.db /media/pi/EMORYSLP/data
   mv data1.csv /media/pi/EMORYSLP/data
   mv excep.log /media/pi/EMORYSLP/data
   cp /dev/null excep.log

   umount /media/pi/EMORYSLP
   resultu=$?
   offLED
   if [ $resultdb -eq 0 -a $resultcsv -eq 0 -a $resultu -eq 0 ];then
      greenLEDon
      sleep 10
      offLED
   else
      redLEDon
      sleep 10
      offLED
   fi
fi
else
 cd /home/pi/mbientlab/Project/calibration
 /home/pi/mbientlab/Project/calibration/executeConnect.sh
 filename=`ls calibrationResults*.csv`
 dosfilename=`echo $filename|sed -e s/://g`
 mv $filename /media/pi/EMORYSLP/data/$dosfilename
 resultdb=$?
 cp excep.log /media/pi/EMORYSLP/data/excepCalibration.log
 cp /dev/null excep.log
 rm data1.db
 rm /media/pi/EMORYSLP/data/calibration.txt
 
 umount /media/pi/EMORYSLP
   resultu=$?
   offLED
   if [ $resultdb -eq 0 -a $resultu -eq 0 ];then
      greenLEDon
      sleep 10
      offLED
   else
      redLEDon
      sleep 10
      offLED
   fi
fi
