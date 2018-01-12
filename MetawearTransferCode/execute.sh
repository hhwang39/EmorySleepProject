#!/bin/bash
PROJECTHOME=/home/pi/mbientlab/Project/Test1
DATAFILE=$PROJECTHOME/data1.db
if [ -f $DATAFILE ]; then
 mv $DATAFILE $DATAFILE.$(/bin/date +"%d%m%Y%H%M")
fi
/usr/bin/sqlite3 $DATAFILE < $PROJECTHOME/createTable.sql
flag=0
while [ $flag -eq 0 ]
do

 string1=$(/bin/date +"%D %T")
 hours=$(/bin/date +"%H")
 if [ $hours -lt 12 ];then
  string2=$(/bin/date -d "+0 days" +"%D")" 12:00:00"
 else
  string2=$(/bin/date -d "+1 days" +"%D")" 12:00:00"
 fi

 StartDate=$(/bin/date -u -d "$string1" +"%s")
 FinalDate=$(/bin/date -u -d "$string2" +"%s")
 diffl=`/usr/bin/expr $FinalDate - $StartDate`
 /bin/echo $(/bin/date +"%D %T")"  python -u test2.py $diffl >> $PROJECTHOME/excep.log" >> $PROJECTHOME/excep.log
 /usr/bin/python -u test2.py $diffl >> $PROJECTHOME/excep.log
 result=$?
 if [ $result -gt 0 ]; then
  flag=0
 fi
 if [ $result -eq 0 ]; then
  flag=1
 fi

done
