# PortaStat
# RPI4 and AD5933 Based Battery Powered, Portable Electrochemical Impedance Spectroscopy Analyzer

## Project Overview
This project implements an Electrochemical Impedance Spectroscopy (EIS) analyzer using a Raspberry Pi 4 and AD5933 impedance converter.  It is designed with a 3-electrode using small signal mechanical relays for gains switching.  Variable clock source for the AD5933 expands the minimum frequency range possible.  Has an external calibration board for compensation of lead inductance and capacitance

### Current Status
- Features a GUI built with Custom Tkinter
- Utilizes the "Impedance" Python library for fitting (planned update for improved robustness)
- Automatic gain switching implemented (currently contains some bugs)

### Short-term Improvements
- Implement progress bars
- Implement supply rail warning system
- fix auto gain control

## Dependencies
- MCP23017 library by Mirko Häberlin
- Impedance 1.7.1
- Custom Tkinter
- numpy
- sympy
- time
- csv

## Contributing
Feel free to contribute to this project by submitting issues or pull requests.
