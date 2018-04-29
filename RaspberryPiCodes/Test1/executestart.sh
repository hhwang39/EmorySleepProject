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
/sbin/hwclock -s
PROJECTHOME=/home/pi/mbientlab/Project/Test1
cd $PROJECTHOME
DATAFILE1=data1
DATAFILE=data1.db
STARTUPFILE=startdate.txt
DEVICEFILE=deviceaddress.txt
if [ ! -f "$STARTUPFILE" ]; then
   /bin/date "+%D %T" > $STARTUPFILE
   cp /dev/null excep.log
fi
  
#if [ -f $DATAFILE ]; then
# mv $DATAFILE $DATAFILE1.$(/bin/date +"%d%m%Y%H%M").db
#fi
#/usr/bin/sqlite3 $DATAFILE < $PROJECTHOME/createTable.sql
initLED
flag=0
while [ $flag -eq 0 ]
do

string1=$(/bin/date +"%D %T")
DATEFROMFILE=`head -1 $STARTUPFILE`
INITTIME=`echo $DATEFROMFILE|awk '{print $2}'`
INITDATE=`echo $DATEFROMFILE|awk '{print $1}'`
string2=$(/bin/date -d "${INITDATE}+7 days" +"%D")" $INITTIME"

 StartDate=$(/bin/date -u -d "$string1" +"%s")
 FinalDate=$(/bin/date -u -d "$string2" +"%s")
 DEVICEADDR=`head -1 $DEVICEFILE`
 diffl=`/usr/bin/expr $FinalDate - $StartDate`
 if [ $diffl -gt 0 ];then
 diff2=`/usr/bin/expr $diffl / 10 `
 blueLEDon
 /bin/echo $(/bin/date +"%D %T")"  python -u qualifyingTest.py $DEVICEADDR $diff2 >> $PROJECTHOME/excep.log" >> $PROJECTHOME/excep.log
 /usr/bin/python -u qualifyingTest.py $DEVICEADDR $diff2 >> $PROJECTHOME/excep.log
 result=$?
 offLED
 if [ $result -gt 0 ]; then
  flag=0
  redLEDon 
  sleep 3
  offLED
 fi
 if [ $result -eq 0 ]; then
  flag=1
 fi
else
 flag=1
fi
done

