#!/bin/bash
string1=$(date +"%D %T")
hours=$(date +"%H")
string2=$(date -d "+0 days" +"%D")" 12:00:00"
echo $string1
echo $string2

StartDate=$(date -u -d "$string1" +"%s")
FinalDate=$(date -u -d "$string2" +"%s")
echo $StartDate
echo $FinalDate
diffl=`expr $FinalDate - $StartDate`
echo $diffl
echo "difference $diffl"
date -u -d "0 $FinalDate sec - $StartDate sec" +"%H:%M:%S"
