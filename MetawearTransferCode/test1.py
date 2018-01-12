# usage: python anonymous_datasignals.py [mac]
from __future__ import print_function
from mbientlab.metawear import MetaWear, libmetawear, parse_value
from mbientlab.metawear.cbindings import *
from time import sleep
from threading import Event
from ctypes import cast, c_char_p
from gattlib import DiscoveryService

import platform
import sys
import sqlite3
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
        i+= 1

    msg = "Select your device (-1 to rescan): "
    selection = int(raw_input(msg) if platform.python_version_tuple()[0] == '2' else input(msg))

address = list(devices)[selection]
print("Connecting to %s..." % (address))
device = MetaWear(address)


device.connect()
print("Connected")
print("Device information: " + str(device.info))
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
libmetawear.mbl_mw_acc_set_odr(device.board, 100.0)
libmetawear.mbl_mw_acc_write_acceleration_config(device.board)
def data_handler(ptr):
    value = parse_value(ptr)
    print({"epoch": ptr.contents.epoch, "value x": value.x, "value y": value.y, "value z": value.z})
    c.execute("INSERT INTO acc VALUES (?,?,?,?)",(ptr.contents.epoch,value.x,value.y,value.z))
    conn.commit()
data_handler_fn = FnVoid_DataP(data_handler)
signal = libmetawear.mbl_mw_acc_get_acceleration_data_signal(device.board)
libmetawear.mbl_mw_datasignal_subscribe(signal, data_handler_fn)
libmetawear.mbl_mw_acc_enable_acceleration_sampling(device.board)
libmetawear.mbl_mw_acc_start(device.board)
print("Stream started")
sleep(30.0)

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
'''sync_event = Event()
result = {}
def handler(board, signals, len):
    result['length'] = len
    result['signals'] = cast(signals, POINTER(c_void_p * len)) if signals is not None else None
    sync_event.set()
handler_fn = FnVoid_VoidP_VoidP_UInt(handler)

class DataHandler:
    def __init__(self, signal):
        raw = libmetawear.mbl_mw_anonymous_datasignal_get_identifier(signal)
        self.identifier = cast(raw, c_char_p).value.decode("ascii")
        self.data_handler_fn = FnVoid_DataP(lambda ptr: print({"identifier": self.identifier, "epoch": ptr.contents.epoch, "value": parse_value(ptr)}))

        libmetawear.mbl_mw_memory_free(raw)

print("Creating anonymous signals")
libmetawear.mbl_mw_settings_set_connection_parameters(metawear.board, 7.5, 7.5, 0, 6000)
sleep(1.0)
libmetawear.mbl_mw_metawearboard_create_anonymous_datasignals(metawear.board, handler_fn)
sync_event.wait()
'''
