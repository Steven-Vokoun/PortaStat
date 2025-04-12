# RPI4 and AD5933 EIS Analyzer

## Project Overview
This project implements an Electrochemical Impedance Spectroscopy (EIS) analyzer using a Raspberry Pi 4 and AD5933 impedance converter. 

### Current Status
- System is mostly functional with room for improvements
- Successfully implemented libraries for AD5933 and multiplexers
- Features a GUI built with Custom Tkinter
- Utilizes the "Impedance" Python library for fitting (planned update for improved robustness)
- Automatic gain switching implemented (currently contains some bugs)

## Planned Improvements

### Short-term Improvements
- Implement internal 5x switchable gains
- Optimize device layout:
  - Relocate screen to left side of enclosure
  - Position power supply adjacent to analog board
  - Add filtering for I2C lines
- Upgrade to double pole relay for 3-electrode switching configuration
- Develop external calibration board for lead inductance and capacitance compensation
- Implement supply rail warning system

### Long-term Goals
- Migrate from Raspberry Pi to lower-power microcontroller
- Reduce overall device footprint
- Design and implement custom battery management board

## Contributing
Feel free to contribute to this project by submitting issues or pull requests.
