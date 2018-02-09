EmorySleepProject
===========
Develop a small portable device and GUI for Patients with Periodic Limb Movement 
## Content Outline
- [**Installation Guide**](#installation-guide)
- [**LED Indictor Status Message**](#led-indicator-of-raspberry-pi)
- [**USB**](#usb)
- [**Interaction with Reciever Module **](#non-automatic-interaction-with-receiver-module-(raspberry-pi))

Installation Guide
------------------
Not written yet
## LED Indicator of Raspberry Pi
RED: Failure to connect \
BLUE: In process of connecting/reconnecting\
GREEN: Connected to Metawear device and received data for at least one cycle
___
## USB
When USB is plugged to the Raspberry Pi there are two cases that can happen
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
2) Since there is nothing to copy, LED will be off

## Non-Automatic Interaction with Receiver Module (Raspberry Pi)
In order to see what is going on with Reciever Module. You have few ways to check
### Windows
