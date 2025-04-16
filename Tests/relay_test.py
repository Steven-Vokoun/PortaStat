from Libraries.MUX_and_CLK_Library import Relays
import time

hardware =  Relays()

resistor_values = ['100', '1k', '10k', '50k', '100k', '500k', '1Meg', '10Meg', 'Randles', 'Counter']
for res in resistor_values:
    print(f"setting calibration to {res}")
    hardware.relays.select_calibration(res)
    time.sleep(30) # in seconds