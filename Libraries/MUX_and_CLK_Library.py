import os
import numpy as np

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
GPA5 = SSR0 = RI0
GPA4 = SSR1 = RI1
GPA3 = SSR2 = RI2

GPA2 = SSR3 = RO0
GPA1 = SSR4 = RO1
GPA0 = SSR5 = RO2

GPB2 = CAL0
GPB3 = CAL1
GPB4 = CAL2
GPB5 = CAL3
GPB6 = CAL4
GPB7 = CAL5
'''

'''
RI0 RI1 RI2
0 0 0 = 10
0 0 1 = 10
0 1 0 = 100
0 1 1 = 100
1 0 0 = 1k
1 0 1 = 10k
1 1 0 = 100k
1 1 1 = 1Meg

RO0 RO1 RO2
0 0 0 = 1k
0 0 1 = 1k
0 1 0 = 5k
0 1 1 = 5k
1 0 0 = 10k
1 0 1 = 50k
1 1 0 = 75k
1 1 1 = 100k

CAL0 CAL1 CAL2 CAL3 CAL4 CAL5
00xxx = 100
01xxx = 1k
100xx = 10k
101xx = 50k
1100x = 100k
1101x = 500k
11100 - 1M
11101 = 10M
11110 = Randles
11111 = Counter
'''


class Calibration_Mux:
    def __init__(self):
        GPIO.setwarnings(False)
        pins = [9,10,22]  # 9 is A2, 10 A1, 22 A0
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    def select_calibration(self, setting):
        if setting == '10Meg' or setting == 10e6 or setting == 0:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
        elif setting == '1Meg' or setting == 1e6 or setting == 1:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
        elif setting == '100k' or setting == 100e3 or setting == 2:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.LOW)
        elif setting == '10k' or setting == 10e3 or setting == 3:
            GPIO.output(9, GPIO.LOW)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.HIGH)
        elif setting == '100' or setting == 100 or setting == 4:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.LOW)
        elif setting == 'Randles' or setting == 5:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.LOW)
            GPIO.output(22, GPIO.HIGH)
        elif setting == 'Counter0' or setting == 6:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.LOW)
        elif setting == 'Counter1' or setting == 7:
            GPIO.output(9, GPIO.HIGH)
            GPIO.output(10, GPIO.HIGH)
            GPIO.output(22, GPIO.HIGH)

class Output_Gain_Mux:
#GPA2 = SSR3 = RO0
#GPA1 = SSR4 = RO1
#GPA0 = SSR5 = RO2

#RO0 RO1 RO2
#0 0 0 = 1k
#0 0 1 = 1k
#0 1 0 = 5k
#0 1 1 = 5k
#1 0 0 = 10k
#1 0 1 = 50k
#1 1 0 = 75k
#1 1 1 = 100k

    def __init__(self, GPIO_Expander, sensor):
        self.GPIO_Expander = GPIO_Expander
        self.sensor = sensor
        GPIO_Expander.digital_write(GPA2, LOW)
        GPIO_Expander.digital_write(GPA1, LOW)
        GPIO_Expander.digital_write(GPA0, LOW)
    def select_gain(self, setting):
        if setting == '1x' or setting == 0:
            GPIO_Expander.digital_write(GPA2, HIGH)
            GPIO_Expander.digital_write(GPA1, HIGH)
            GPIO_Expander.digital_write(GPA0, HIGH)
        elif setting == '.75x' or setting == 1:
            GPIO_Expander.digital_write(GPA2, HIGH)
            GPIO_Expander.digital_write(GPA1, HIGH)
            GPIO_Expander.digital_write(GPA0, LOW)
        elif setting == '.5x' or setting == 2:
            GPIO_Expander.digital_write(GPA2, HIGH)
            GPIO_Expander.digital_write(GPA1, LOW)
            GPIO_Expander.digital_write(GPA0, HIGH)
        elif setting == '.1x' or setting == 3:
            GPIO_Expander.digital_write(GPA2, HIGH)
            GPIO_Expander.digital_write(GPA1, LOW)
            GPIO_Expander.digital_write(GPA0, LOW)
        elif setting == '.05x' or setting == 4:
            GPIO_Expander.digital_write(GPA2, LOW)
            GPIO_Expander.digital_write(GPA1, HIGH)
            GPIO_Expander.digital_write(GPA0, LOW)
        elif setting == '.01x' or setting == 5:
            GPIO_Expander.digital_write(GPA2, LOW)
            GPIO_Expander.digital_write(GPA1, LOW)
            GPIO_Expander.digital_write(GPA0, LOW)

class Input_Gain_Mux:
#GPA5 = SSR0 = RI0
#GPA4 = SSR1 = RI1
#GPA3 = SSR2 = RI2

#RI0 RI1 RI2
#0 0 0 = 10
#0 0 1 = 10
#0 1 0 = 100
#0 1 1 = 100
#1 0 0 = 1k
#1 0 1 = 10k
#1 1 0 = 100k
#1 1 1 = 1Meg

    def __init__(self, GPIO_Expander, sensor):
        pins = [24,23]  # 24 is A1, 23 is A0
        GPIO.setmode(GPIO.BCM)
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
    def select_gain(self, setting):
        if setting == '100x' or setting == 100 or setting == 0:
            GPIO.output(24, GPIO.LOW)
            GPIO.output(23, GPIO.LOW)
        elif setting == '10kx' or setting == 10e3 or setting == 1:
            GPIO.output(24, GPIO.LOW)
            GPIO.output(23, GPIO.HIGH)
        elif setting == '100kx' or setting == 100e3 or setting == 2:
            GPIO.output(24, GPIO.HIGH)
            GPIO.output(23, GPIO.LOW)
        elif setting == '1Mx' or setting == 1e6 or setting == 3:
            GPIO.output(24, GPIO.HIGH)
            GPIO.output(23, GPIO.HIGH)