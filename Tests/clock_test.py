import sys
sys.path.append('../')
from Libraries.MUX_and_CLK_Library import LTC6904
import numpy as np
import time

clk =  LTC6904()

freqs = np.linspace(50_000, 20_000, 30_000, 100_000)
for freq in freqs:
    clk.Turn_On_Clock(freq)
    time.sleep(15)