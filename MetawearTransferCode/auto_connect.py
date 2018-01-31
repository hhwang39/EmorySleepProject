from mbientlab.metawear import MetaWear, libmetawear
from mbientlab.metawear.cbindings import *
from gattlib import DiscoveryService
import time


selection = False
devices = None

while not selection:
    service = DiscoveryService("hci0")
    devices = service.discover(2)
    #print(devices)

    i = 0
    for address, attr in devices.items():
        print("[%d] %s (%s)" % (i, address, attr['name']))
        if attr['name'] == 'MetaWear':
            print(address)
            #hardcode
            mw_addr = "F6:0D:1B:10:04:FC"
            selection = True
            break
        i+= 1
    #selection = int(raw_input(msg))
    time.sleep(5.0)

print("Connecting to %s..." % (mw_addr))
device = MetaWear(mw_addr)
time.sleep(5.0)

flag = False
while not flag:
    try:
        device.connect()
        print("Connected")
        print("Device information: " + str(device.info))
        print("\n test \n")
        flag = True
    except Exception as e:
        time.sleep(1.0)
        print(e)
                    
# grab the first scanned device
#address = devices.items()[0][0]
#address = "F6:0D:1B:10:04:FC"
#device = MetaWear(address)
#status = device.connect()

pattern= LedPattern(repeat_count= 10)
libmetawear.mbl_mw_led_load_preset_pattern(byref(pattern), LedPreset.BLINK)
libmetawear.mbl_mw_led_write_pattern(device.board, byref(pattern), LedColor.RED)
time.sleep(10.0)
libmetawear.mbl_mw_led_stop_and_clear(device.board)
libmetawear.mbl_mw_led_play(device.board)
time.sleep(1.0)

libmetawear.mbl_mw_settings_set_connection_parameters(device.board, 7.5, 7.5, 0, 6000)
raw = libmetawear.mbl_mw_metawearboard_get_model_name(device.board)
sleep(1.0)
model_name = cast(raw, c_char_p).value.decode("ascii")
print("model="+model_name)

time.sleep(30.0)
print("Disconnecting")
device.disconnect()
