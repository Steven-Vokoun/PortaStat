import os
import numpy as np
from Libraries.mcp23017 import MCP23017

GPA0 = 0
GPA1 = 1
GPA2 = 2
GPA3 = 3
GPA4 = 4
GPA5 = 5
GPA6 = 6
GPA7 = 7
GPB0 = 8
GPB1 = 9
GPB2 = 10
GPB3 = 11
GPB4 = 12
GPB5 = 13
GPB6 = 14
GPB7 = 15
ALL_GPIO = {
    "Cal Board": [GPB2, GPB3, GPB4, GPB5, GPB6],
    "Output": [GPA2, GPA1, GPA0],
    "Input": [GPA5, GPA4, GPA3],
    "Other": [GPA6, GPA7, GPB0, GPB1, GPB7]
}

HIGH = 0xFF
LOW = 0x00


try:
    from smbus2 import SMBus
    import RPi.GPIO as GPIO
except ImportError:
    if os.name == 'nt':  # Check if the operating system is Windows
        print("smbus2 library is not supported on Windows, using dummy class instead...")
    else:
        ValueError("smbus2 library is not installed")

class LTC6904:
    #DEFINITIONS
    LTC6904_ADDRESS = 0x17  # I2C address of the LTC6904

    LTC6904_CLK_ON_CLK_INV_ON   = 0x00    # Clock on, inverted clock on
    LTC6904_CLK_OFF_CLK_INV_ON  = 0x01    # Clock off, inverted clock on
    LTC6904_CLK_ON_CLK_INV_OFF  = 0x02    # Clock on, inverted clock off
    LTC6904_POWER_DOWN          = 0x03    # Powers down clocks

    #FUNCTIONS
    def __init__(self):
        self.bus = SMBus(1)

    def write_registers(self, MS, LS):
        self.bus.write_byte_data(self.LTC6904_ADDRESS, MS, LS)

    def Turn_On_Clock(self, frequency):
        OCT = int(3.322 * np.log10(frequency / 1039))
        DAC = 2048 - int((2078 * (2 ** (10+OCT))) / frequency)
        MS = OCT << 4 | DAC >> 4
        LS = DAC << 4 | self.LTC6904_CLK_ON_CLK_INV_OFF
        self.write_registers(MS, LS)

    def Turn_Off_Clock(self):
        MS = 0x00
        LS = self.LTC6904_POWER_DOWN
        self.write_registers(MS, LS)

'''
INPUTS:                 OUTPUTS:                CALIBRATION:
GPA5 = SSR0 = RI0       GPA2 = SSR3 = RO0	    GPB2 = CAL0
GPA4 = SSR1 = RI1	    GPA1 = SSR4 = RO1	    GPB3 = CAL1
GPA3 = SSR2 = RI2	    GPA0 = SSR5 = RO2	    GPB4 = CAL2
		                                        GPB5 = CAL3
		                                        GPB6 = CAL4

RI0 RI1 RI2	            RO0 RO1 RO2	            CAL0 CAL1 CAL2 CAL3 CAL4
0 0 0 = 10	            0 0 0 = 1k	            00xxx = 100
0 0 1 = 10	            0 0 1 = 1k	            01xxx = 1k
0 1 0 = 100	            0 1 0 = 5k	            100xx = 10k
0 1 1 = 100	            0 1 1 = 5k	            101xx = 50k
1 0 0 = 1k	            1 0 0 = 10k	            1100x = 100k
1 0 1 = 10k	            1 0 1 = 50k	            1101x = 500k
1 1 0 = 100k	        1 1 0 = 75k	            11100 - 1M
1 1 1 = 1Meg	        1 1 1 = 100k	        11101 = 10M
		                                        11110 = Randles
		                                        11111 = Counter
'''

class Relays:
    def __init__(self):
        self.mcp = MCP23017()
        # init relevant pins LOW
        relevant_gpio = ALL_GPIO["Cal Board"] + ALL_GPIO["Output"] + ALL_GPIO["Input"]
        for pin in relevant_gpio:
            self.mcp.digital_write(pin, LOW)

    def select_calibration(self, setting):
        if setting == '100' or setting == 100 or setting == 0:
            self.mcp.digital_write(GPB2, LOW)
            self.mcp.digital_write(GPB3, LOW)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, LOW)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '1k' or setting == 1e3 or setting == 1:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, LOW)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, LOW)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '10k' or setting == 10e3 or setting == 2:
            self.mcp.digital_write(GPB2, LOW)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, LOW)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '50k' or setting == 50e3 or setting == 3:
            self.mcp.digital_write(GPB2, LOW)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, HIGH)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '100k' or setting == 100e3 or setting == 4:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, LOW)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '500k' or setting == 500e3 or setting == 5:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, HIGH)
            self.mcp.digital_write(GPB5, LOW)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '1Meg' or setting == 1e6 or setting == 6:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, HIGH)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == '10Meg' or setting == 10e6 or setting == 7:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, LOW)
            self.mcp.digital_write(GPB5, HIGH)
            self.mcp.digital_write(GPB6, HIGH)
        elif setting == 'Randles' or setting == 8:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, HIGH)
            self.mcp.digital_write(GPB5, HIGH)
            self.mcp.digital_write(GPB6, LOW)
        elif setting == 'Counter' or setting == 9:
            self.mcp.digital_write(GPB2, HIGH)
            self.mcp.digital_write(GPB3, HIGH)
            self.mcp.digital_write(GPB4, HIGH)
            self.mcp.digital_write(GPB5, HIGH)
            self.mcp.digital_write(GPB6, HIGH)

    def set_output_gain(self, setting):
        if setting == '1x' or setting == 0:
            self.mcp.digital_write(GPA2, HIGH)
            self.mcp.digital_write(GPA1, HIGH)
            self.mcp.digital_write(GPA0, HIGH)
        elif setting == '.75x' or setting == 1:
            self.mcp.digital_write(GPA2, HIGH)
            self.mcp.digital_write(GPA1, HIGH)
            self.mcp.digital_write(GPA0, LOW)
        elif setting == '.5x' or setting == 2:
            self.mcp.digital_write(GPA2, HIGH)
            self.mcp.digital_write(GPA1, LOW)
            self.mcp.digital_write(GPA0, HIGH)
        elif setting == '.1x' or setting == 3:
            self.mcp.digital_write(GPA2, HIGH)
            self.mcp.digital_write(GPA1, LOW)
            self.mcp.digital_write(GPA0, LOW)
        elif setting == '.05x' or setting == 4:
            self.mcp.digital_write(GPA2, LOW)
            self.mcp.digital_write(GPA1, HIGH)
            self.mcp.digital_write(GPA0, LOW)
        elif setting == '.01x' or setting == 5:
            self.mcp.digital_write(GPA2, LOW)
            self.mcp.digital_write(GPA1, LOW)
            self.mcp.digital_write(GPA0, LOW)

    def set_input_gain(self, setting):
        if setting == '10x' or setting == 10 or setting == 0:
            self.mcp.digital_write(GPA5, LOW)
            self.mcp.digital_write(GPA4, LOW)
            self.mcp.digital_write(GPA3, LOW)
        elif setting == '100x' or setting == 100 or setting == 1:
            self.mcp.digital_write(GPA5, LOW)
            self.mcp.digital_write(GPA4, HIGH)
            self.mcp.digital_write(GPA3, LOW)
        elif setting == '1kx' or setting == 1e3 or setting == 2:
            self.mcp.digital_write(GPA5, HIGH)
            self.mcp.digital_write(GPA4, LOW)
            self.mcp.digital_write(GPA3, LOW)
        elif setting == '10kx' or setting == 10e3 or setting == 3:
            self.mcp.digital_write(GPA5, HIGH)
            self.mcp.digital_write(GPA4, LOW)
            self.mcp.digital_write(GPA3, HIGH)
        elif setting == '100kx' or setting == 100e3 or setting == 4:
            self.mcp.digital_write(GPA5, HIGH)
            self.mcp.digital_write(GPA4, HIGH)
            self.mcp.digital_write(GPA3, LOW)
        elif setting == '1Megx' or setting == 1e6 or setting == 5:
            self.mcp.digital_write(GPA5, HIGH)
            self.mcp.digital_write(GPA4, HIGH)
            self.mcp.digital_write(GPA3, HIGH)