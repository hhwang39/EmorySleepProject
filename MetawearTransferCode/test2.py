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

def getStatusFn(event, status):
    if status != 0:
        print("Error recording commands, status= %s" % status)
    else :
        print( "Commands recorded" )

callback_type = ctypes.CFUNCTYPE(None,ctypes.c_void_p, ctypes.c_int)        

getStatusFn_handler_fn = callback_type(getStatusFn)
pattern= LedPattern(repeat_count= 10)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)

def setup_dc_event(device) :

    # Setup disconnect event to blink the blue led 10x when fired
    dc_event = libmetawear.mbl_mw_settings_get_disconnect_event(device.board)
    libmetawear.mbl_mw_event_record_commands(dc_event);
    #libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.BLUE)
    #libmetawear.mbl_mw_led_play(device.board)
    libmetawear.mbl_mw_debug_reset(device.board)
    libmetawear.mbl_mw_event_end_record(dc_event, getStatusFn_handler_fn)

def data_handler(ptr):
        value = parse_value(ptr)
        print({"epoch": ptr.contents.epoch, "value x": value.x, "value y": value.y, "value z": value.z})
        c.execute("INSERT INTO acc VALUES (?,?,?,?)",(ptr.contents.epoch,value.x,value.y,value.z))
        conn.commit()
data_handler_fn = FnVoid_DataP(data_handler)



try:
    difftime=sys.argv[1]

    conn = sqlite3.connect('data1.db', check_same_thread=False)
    c = conn.cursor()

    selection = -1
    devices = None

    while selection == -1:
        service = DiscoveryService("hci0")
        devices = service.discover(2)
        print(devices)


        i = 0
        for address, attr in devices.items():
            print("[%d] %s (%s)" % (i, address, attr['name']))
            if attr['name'] == "MetaWear":
                selection=i
            i+= 1
        if selection == -1:
            msg = "Select your device (-1 to rescan): "
            selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))  

    

    address = list(devices)[selection]
    print("Connecting to %s..." % (address))
    device = MetaWear(address)


    device.connect()
    print("Connected")
    print("Device information: " + str(device.info))
    sleep(5.0)
    setup_dc_event(device)
    sleep(5.0)
    pattern= LedPattern(repeat_count= 10)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.RED)
    libmetawear.mbl_mw_led_play(device.board)

    sleep(5.0)

    libmetawear.mbl_mw_led_stop_and_clear(device.board)
    sleep(1.0)

    libmetawear.mbl_mw_settings_set_connection_parameters(device.board, 7.5, 7.5, 0, 6000)

    raw = libmetawear.mbl_mw_metawearboard_get_model_name(device.board)
    sleep(1.0)
    model_name = cast(raw, c_char_p).value.decode("ascii")

    print("model="+model_name)

# Stream data at 100Hz
    libmetawear.mbl_mw_acc_set_range(device.board, 16.0)
    libmetawear.mbl_mw_acc_set_odr(device.board, 12.5)
    libmetawear.mbl_mw_acc_write_acceleration_config(device.board)
    
    signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device.board)
    libmetawear.mbl_mw_datasignal_subscribe(signal, data_handler_fn)
    libmetawear.mbl_mw_acc_enable_acceleration_sampling(device.board)
    libmetawear.mbl_mw_acc_start(device.board)
    print("Stream started")
    sleep(float(difftime))

# Stop the stream

    libmetawear.mbl_mw_acc_stop(device.board)
    libmetawear.mbl_mw_acc_disable_acceleration_sampling(device.board)
    libmetawear.mbl_mw_datasignal_unsubscribe(signal)
    sleep(1.0)
    conn.close()
    sleep(1.0)
    device.disconnect()
    sleep(1.0)
    print("Disconnected") 

except:
    print (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Unexpected error:",sys.exc_info()[0])
    sys.exit(1)
