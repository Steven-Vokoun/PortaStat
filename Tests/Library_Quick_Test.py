import sys
sys.path.append('../')
from Libraries.AD5933_Library import AD5933
from Libraries.MUX_and_CLK_Library import Relays, LTC6904
relays =  Relays()

#Set Calibration
class HardwareComponents:
    def __init__(self, dummy):
        self.sensor = AD5933() if not dummy else type('DummySensor', (), {
                        'measure_temperature': lambda: 25,
                        'send_cmd': lambda x: None,
                        'set_output_voltage': lambda x,y: None,
                        'Calibration_Sweep': lambda a,b,c,d,e,f,g: [0]*3
                    })()
        self.CLK = LTC6904() if not dummy else type('DummyCLK', (), {
                        'Turn_On_Clock': lambda x: None
                    })()
hardware = HardwareComponents(dummy=False)

Resistor = 220_000
hardware.sensor.set_increment_number(0)
hardware.sensor.set_settling_time_cycles(1000)
print('Calibrating')
Cal_Freqs, Gain_Factors, Sys_Phases = hardware.sensor.Calibration_Sweep(Resistor, 5_000, 105_000, 200, hardware, spacing_type='linear')
print('Sweeping')
freqs, real, imag = hardware.sensor.Complete_Sweep(10_000, 100_000, 200, hardware, spacing_type='linear')
print('Adjusting')
Magnitude = hardware.sensor.Adjust_Magnitude_Return_abs_Impedance(freqs, real, imag, Cal_Freqs, Gain_Factors)
Phase = hardware.sensor.Adjust_Phase_Return_Phase(freqs, real, imag, Cal_Freqs, Sys_Phases)

import matplotlib.pyplot as plt

print('Plotting')
fig, axs = plt.subplots(2, 1)

axs[0].plot(freqs, Magnitude)
axs[0].set_xlabel('Frequency (Hz)')
axs[0].set_ylabel('Impedance (Ohms)')

axs[1].plot(freqs, Phase)
axs[1].set_xlabel('Frequency (Hz)')
axs[1].set_ylabel('Phase (Degrees)')

plt.tight_layout()

plt.show()