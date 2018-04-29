# usage: python anonymous_datasignals.py [mac]
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event
from ctypes import *
from gattlib import DiscoveryService

import ctypes

import platform
import sys
from datetime import datetime
import sqlite3

from threading import Timer
from time import sleep
import os
import signal

from subprocess import call
#import RPi.GPIO as GPIO

#global variables used within code.
# Watchdog timer counter and timeout variable. Used to specify for watchdog to run for 10 seconds.
counter=0
oldcounter=0
timeout=10
wdvar=None
# Initialize battery signal variable 
bsignal=None
# Initialize battery percentage to 100.
voltagelevel=100

# Watchdog timer class
class Watchdog:
    def __init__(self, timeout, userHandler=None):  # timeout in seconds
        self.timeout = timeout
        self.handler = userHandler if userHandler is not None else self.defaultHandler
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def reset(self):
        self.timer.cancel()
        self.timer = Timer(self.timeout, self.handler)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def defaultHandler(self):
        raise self

		# Watchdog calls exception using os.kill when counter is stuck. This occurs after 10 seconds.
def mywatchdog():
    global oldcounter
    global counter
    if oldcounter == counter:
	    # Print on console time data was not received.
        print( datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"no data recevied in",timeout,"seconds")
        os.kill(os.getpid(), signal.SIGINT)
    else:
        oldcounter=counter
        wdvar.reset() 

# Status Handler used for stating success or failure of commands stored in MetaWear
def getStatusFn(event, status):
    if status != 0:
        print("Error recording commands, status= %s" % status)
    else :
        print( "Commands recorded" )
# C++ wrapper calls for Python calling pointer to Status Handler using ctypes. 
callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p, ctypes.c_int)        
getStatusFn_handler_fn = callback_type(getStatusFn)

#pattern= LedPattern(repeat_count= 10)
#libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)

# Disconnect Event Handler used to reset Metawear before starting a new accelerometer sampling connection.
# This ensures minimal issues with memory management with pointers.
def setup_dc_event(device) :

    # Setup disconnect event to blink the blue led 10x when fired
    dc_event = libmetawear.mbl_mw_settings_get_disconnect_event(device.board)
    libmetawear.mbl_mw_event_record_commands(dc_event)
    #libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.BLUE)
    #libmetawear.mbl_mw_led_play(device.board)
    libmetawear.mbl_mw_debug_reset(device.board)
    libmetawear.mbl_mw_event_end_record(dc_event, getStatusFn_handler_fn)

# Battery Handler used to print value of battery percentage to console.
def batt_handler(ptr):
    global voltagelevel
    value = parse_value(ptr)
    print({"voltage": value.charge})
    voltagelevel=value.charge
# C++ wrapper calls for Python calling pointer to Battery Handler using ctypes. 	
batt_handler_fn = FnVoid_DataP(batt_handler)
 
# Timer Event Handler used to read and subscribe to battery state data signal. This allows MetaWear device
# to read the battery voltage as specified by the timer_start function, which is referenced from timer_setup function.
def timer_created(timer):
    global bsignal
    bsignal = libmetawear.mbl_mw_settings_get_battery_state_data_signal(device.board)
    libmetawear.mbl_mw_datasignal_subscribe(bsignal, batt_handler_fn)
    libmetawear.mbl_mw_event_record_commands(timer)
    libmetawear.mbl_mw_datasignal_read(bsignal)
    libmetawear.mbl_mw_event_end_record(timer, getStatusFn_handler_fn)
    libmetawear.mbl_mw_timer_start(timer)

# C++ wrapper calls for Python calling pointer to Timer Event Handler using ctypes. 
callback_type2 = ctypes.CFUNCTYPE(None,ctypes.c_void_p)        
timer_created_fn = callback_type2(timer_created)


# Setup Timer function to program MetaWear device to read the battery voltage every 5 seconds.    
def timer_setup(device) :

    # Setup timer to read battery level
    libmetawear.mbl_mw_timer_create_indefinite(device.board, 5000, 0,timer_created_fn)

# Data Handler used to read the accelerometer data from the MetaWear device as well as store the data to
# a database file using sqlite3. 
def data_handler(ptr):
    global counter
    value = parse_value(ptr)
    print({"epoch": ptr.contents.epoch})
    c.execute("INSERT INTO acc VALUES (?,?,?,?)",(ptr.contents.epoch,value.x,value.y,value.z))
    conn.commit()
	#Watchdog timer counter variable.
    counter+=1
# C++ wrapper calls for Python calling pointer to Data Handler using ctypes.	
data_handler_fn = FnVoid_DataP(data_handler)


# Try Portion of Code used to attempt communication and storage of data with MetaWear Device.
try:
    # Difftime is the amount of seconds the accelerometer will sample data
    myaddress=sys.argv[1]
    difftime=sys.argv[2]
	# Setting GPIO Mode to use BCM pin numbers
    #GPIO.setmode(GPIO.BCM)
	# Disable warnings for GPIO pins
    #GPIO.setwarnings(False)
	# Initialize red, green, and blue LED pins 
    redLED=23
    greenLED=22
    blueLED=24
    channels=[greenLED, blueLED]
	# Set green and blue led to output pins.
    #GPIO.setup(channels,GPIO.OUT)

	# Initializes sqlite3 to create/connect to a data1.db file
    conn = sqlite3.connect('data1.db', check_same_thread=False)
    # cursor for sqlite3
    c = conn.cursor()
	# Creates table inside data1.db if it does not exist already
    c.execute("CREATE TABLE IF NOT EXISTS acc ( epoch INTEGER NOT NULL, valuex REAL, valuey REAL, valuez REAL )")

	# Initialize variables for automatic Bluetooth connection and selection of MetaWear Device
    selection = -1
    devices = None

	# Prints Table of available bluetooth devices and connects to the first MetaWear device it sees.
    while selection == -1:
        service = DiscoveryService("hci0")
        devices = service.discover(2)
        print(devices)


        i = 0
        for address, attr in devices.items():
            print("[%d] %s (%s)" % (i, address, attr['name']))
            #if attr['name'] == "MetaWear":
            if address == myaddress:
                selection=i
            i+= 1
		# If MetaWear is not seen, call exception	
        if selection == -1:
            print( datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"device not detected")
	    os.kill(os.getpid(), signal.SIGINT)  

    
     # MAC Address extracted during Discovery service connection
    address = list(devices)[selection]
    print("Connecting to %s..." % (address))
	# Initialize MetaWear object with MAC address.
    device = MetaWear(address)

    # Connect to MetaWear 
    device.connect()
    #device._btle_connection.on_disconnect=getStatusFn_handler_fn
    print("Connected")
    print("Device information: " + str(device.info))
    sleep(5.0)
	# Call Disconnect Event Handler
    setup_dc_event(device)
    sleep(5.0)
	# MetaWear blinks Red 10 times
    pattern= LedPattern(repeat_count= 10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.RED)
    libmetawear.mbl_mw_led_play(device.board)

    sleep(5.0)

    libmetawear.mbl_mw_led_stop_and_clear(device.board)
    sleep(1.0)
	
	# Sets connection parameters such as latency, minimum, and maximum interval duration.
    libmetawear.mbl_mw_settings_set_connection_parameters(device.board, 7.5, 7.5, 0, 6000)
	
	# Get MetaWear Model Number
    raw = libmetawear.mbl_mw_metawearboard_get_model_name(device.board)
    sleep(1.0)
    model_name = cast(raw, c_char_p).value.decode("ascii")

    print("model="+model_name)

# Stream data at 12.5Hz and set range to +-16g
    libmetawear.mbl_mw_acc_set_range(device.board, 16.0)
    libmetawear.mbl_mw_acc_set_odr(device.board, 12.5)
    libmetawear.mbl_mw_acc_write_acceleration_config(device.board)
    
	# Initialize cycles running using difftime variable specified. This tells how long to sample data.
    cycles=int(difftime)
	# Start timer event for reading battery voltage.
    timer_setup(device)
    sleep(8.0)
	
	# Initializes and turns on accelerometer
    msignal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device.board)
    libmetawear.mbl_mw_datasignal_subscribe(msignal, data_handler_fn)
    libmetawear.mbl_mw_acc_enable_acceleration_sampling(device.board)
    libmetawear.mbl_mw_acc_start(device.board)
    print("Stream started")
	# Starts Watchdog timer
    wdvar=Watchdog(timeout,mywatchdog)
    flagfirstcycle=0

    retcode = call("python -u calibrationProcess.py "+address,shell=True)
    print("exit with code",retcode)
    
    # Turn off MetaWear at specified battery percentage
    '''while cycles>0:
        print("cycles %d"%cycles)
        if voltagelevel < 6:
           cycles=1  
        sleep(10.0)
        # After 1 cycle, turn Raspberry Pi LED green to indicate successful connection.
        if flagfirstcycle==0:
           #GPIO.output(blueLED, GPIO.LOW)
           #GPIO.output(greenLED, GPIO.HIGH)
           flagfirstcycle=1
        cycles=cycles-1'''
   # sleep(float(difftime))
    # Stop Watchdog timer after set cycle time.
    wdvar.stop()

# Stop the data stream and closes connection.

    libmetawear.mbl_mw_acc_stop(device.board)
    libmetawear.mbl_mw_acc_disable_acceleration_sampling(device.board)
    libmetawear.mbl_mw_datasignal_unsubscribe(msignal)
    libmetawear.mbl_mw_datasignal_unsubscribe(bsignal)
    sleep(1.0)
    conn.close()
    sleep(1.0)
    device.disconnect()
    sleep(1.0)
    print("Disconnected")
    if retcode != 0:
        sys.exit(retcode)
except TypeError as e:
    print (e)
    raise
except ArgumentError as e:
    print(e)
    raise
except:
    # If exception happens during try portion, stop the data stream and close the connection.
    print (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Unexpected error:",sys.exc_info()[0])
# Stop the stream

    libmetawear.mbl_mw_acc_stop(device.board)
    libmetawear.mbl_mw_acc_disable_acceleration_sampling(device.board)
    libmetawear.mbl_mw_datasignal_unsubscribe(msignal)
    libmetawear.mbl_mw_datasignal_unsubscribe(bsignal)
    sleep(1.0)
    conn.close()
    sleep(1.0)
    device.disconnect()
    sleep(1.0)
    print("Disconnected") 
    #os.kill(os.getpid(), signal.SIGINT)  
    sys.exit(1)
