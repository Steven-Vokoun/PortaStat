import sys
sys.path.append('../')
from Libraries.MUX_and_CLK_Library import Relays
import time

relays =  Relays()

resistor_values = ['10x', '100x', '1kx', '10kx', '100kx', '1Megx']
for res in resistor_values:
    print(f"setting calibration to {res}")
    relays.set_input_gain(res)
    time.sleep(30) # in seconds