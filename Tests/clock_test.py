from Libraries.MUX_and_CLK_Library import LTC6904
import numpy as np
import time

clk =  LTC6904()

freqs = np.linspace(10_000, 16.776e3, 100)
for freq in freqs:
    sys_clk = min(freq * 1_000, 16.776e6)
    clk.Turn_On_Clock(freq)
    time.sleep(30)