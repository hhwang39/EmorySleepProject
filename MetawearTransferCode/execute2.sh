#!/bin/bash
flag=0
while [ $flag -eq 0 ]
do

 string1=$(date +"%D %T")
 hours=$(date +"%H")
 if [ $hours -lt 12 ];then
  string2=$(date -d "+0 days" +"%D")" 12:00:00"
 else
  string2=$(date -d "+1 days" +"%D")" 12:00:00"
 fi

 StartDate=$(date -u -d "$string1" +"%s")
 FinalDate=$(date -u -d "$string2" +"%s")
 diffl=`expr $FinalDate - $StartDate`
 echo $(date +"%D %T")"  python -u testexcep.py $diffl >> excep.log" >> excep.log
 python -u testexcep.py 0 >> excep.log
 result=$?
 if [ $result -gt 0 ]; then
  flag=0
 fi
 if [ $result -eq 0 ]; then
  flag=1
 fi

done
