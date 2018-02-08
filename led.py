from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService

from time import sleep



b_id = "F6:0D:1B:10:04:FC"
flag = True
status = None
log = open("helloWorld.txt", "w+")
log.write("Start\n")
log.flush()
sleep(10.0)
service = DiscoveryService("hci0")
devices = service.discover(2)
for addr, attr in devices.items():
    print("{}, {}".format(addr, attr["name"]))
    log.write("{}, {}\n".format(addr, attr["name"]))
device = MetaWear(b_id)
while flag:
        try:
            
            print("Connecting ...")
            log.write("Connecting...\n")
            log.flush()
            sleep(5.0)
            device.connect()
            print(device.info)
            print("Connected!")
            log.write("Connected...\n")
            log.flush()
            flag = False
            sleep(5.0)
        except Exception as e:
            print("Connection failed Reconnecting ...")
            log.write("Connection failed Reconnecting ...\n")
            log.flush()
            sleep(20.0)
   
if not flag:        
    battery_id = "00002a19-0000-1000-8000-00805f9b34fb"
    battery_level = device.gatt.read_by_uuid(battery_id)[0]
    print(ord(battery_level))
    pattern = LedPattern(repeat_count=Const.LED_REPEAT_INDEFINITELY)
    libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
    libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.GREEN)
    libmetawear.mbl_mw_led_play(device.board)
    sleep(5.0)
    libmetawear.mbl_mw_led_stop_and_clear(device.board)
    sleep(2.0)
    device.disconnect()
    sleep(2.0)
a.close()
