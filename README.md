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
All libraries and codes needed to be installed on Raspberry Pi are listed out under installationSteps.txt file.

The main Python code along with calibration setup code needs to be set up under directory /home/pi/mbientlab/Project.

A copy of codes can be found under RaspberryPiCodes. The folders calibration and Test1 should be placed under directory previously specified. 

Inside services folder, the two .service files should be placed under directory /etc/systemd/system of Raspberry Pi 3.
These services calls files within Project folder that runs main MetaWear connection during boot up.

## LED Indicator of Raspberry Pi 

### Normal
Normal Mode is active when power is plugged in to Raspberry Pi. 

### Light Indicator (Normal)
RED: Failure to connect \
BLUE: In process of connecting/reconnecting\
GREEN: Connected to Metawear device and has received data for at least one cycle

### Calibration Mode
Calibration Mode is active when USB drive contains a blank calibration.txt file inside data folder.
USB drive must be plugged in to Raspberry Pi 3 during entire process.

### Light Indicator (Calibration)
In Process of Connecting:\
RED: Failure to connect \
BLUE: In process of connecting/reconnecting

Once Connected (In Sequence):\
MAGENTA: Stays on for 30 seconds to place MetaWear facing +Z direction \
CYAN: Stays on for 15 seconds to place MetaWear facing -Z direction\
YELLOW: Stays on for 15 seconds to place MetaWear facing +Y direction\
WHITE: Stays on for 15 seconds to place MetaWear facing -Y direction\
RED: Stays on for 15 seconds to place MetaWear facing +X direction\
BLUE: Stays on for 15 seconds to place MetaWear facing -X direction\
WHITE: Indicates calibration process complete and in process of calculating values

LED will turn off and then turn blue to indicate process of transferring files to USB.\
LED will turn Green indicating that 3 files were transferred to the USB:\
calibrationResultsXXXXXXXXXXXX.csv - CSV file containing calibration offset and gains 
excepCalibration.log - log file containing lines printed from RPI terminal.

## USB
When a USB drive is plugged in to the Raspberry Pi, there are three cases that can happen
The 3 files transferred to the USB are:\
excep.log - log file containing lines printed from RPi terminal.\
data1.db - SQLite file containing the database\
data1.csv - the same data as data1.db in a csv format\

Besides these files, a backup folder is created as well within Test1 folder called "backup"\
where backup of data1.db file is stored.
#### 1. USB is plugged in after completion of the program
1) LED will be off, indicating USB is recognized.
2) LED turns blue indicating that the Receiver Module is in the process of copying
3) LED turns green indicating a successful file transfer
#### 2. USB is plugged during in as program is running
1) Program will be terminated
2) LED will be off, indicating USB is recognized.
3) LED turns blue indicating that the Receiver Module is in the process of copying
4) LED turns green indicating a successful file transfer
#### 3. USB is plugged in again after transfer is completed
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
