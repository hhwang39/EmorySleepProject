EmorySleepProject
===========
Develop a small portable device and GUI for Patients with Periodic Limb Movement 
## Content Outline
- [**Installation Guide**](#installation-guide)
- [**LED Indicator Status Message**](#led-indicator-of-raspberry-pi)
- [**USB**](#usb)
- [**Interaction with Receiver Module**](#non-automatic-interaction-with-receiver-module-raspberry-pi)
  * [**Windows**](#windows)
  * [**Ubuntu (Linux)**](#ubuntu)
- [**Trouble Shooting**](#troubleshooting)

Installation Guide
------------------
Not written yet
## LED Indicator of Raspberry Pi
RED: Failure to connect \
BLUE: In process of connecting/reconnecting\
GREEN: Connected to Metawear device and has received data for at least one cycle
___
## USB
When a USB drive is plugged to the Raspberry Pi, there are two cases that can happen
The 3 files transferred to the USB are:\
excep.log - log file containing lines printed from RPi terminal.\
data1.db - SQLite file containing the database\
data1.csv - the same data as data1.db in a csv format\
#### 1. USB is plugged after completion of the program
1) LED will be off, indicating USB is recognized.
2) LED turns blue indicating that the Receiver Module is in the process of copying
3) LED turns green indicating a successful file transfer
#### 2. USB is plugged during program running
1) Program will be terminated
2) LED will be off, indicating USB is recognized.
3) LED turns blue indicating that the Receiver Module is in the process of copying
4) LED turns green indicating a successful file transfer
#### 2. USB is plugged again after transfer is completed
1) LED turns blue indicating that the Receiver Module is in the process of copying
2) Since there is nothing to copy, the LED will be off

## Non-Automatic Interaction with Receiver Module (Raspberry Pi)
There are a number of ways to interface with the Receiver Module (RPi) directly. The easiest way is to connect a monitor to the RPi and thus directly display the contents through the use of an HDMI cable. This method however requires a keyboard and mouse. The alternative option is to SSH into the RPi using either the terminal or a program (Putty) only after knowing the IP address of the RPi.
### Windows
* [***Putty***](https://www.putty.org/)
### Ubuntu
* [***ssh***](https://www.ssh.com/ssh/command/)
```
ssh pi@(ip of raspberry pi)
```

## Troubleshooting
Within the /home/pi/mbientlab/Project/Test1/ directory a log file named excep.log exists which contains the entire piped output of the python program including any errors that might have occured.
