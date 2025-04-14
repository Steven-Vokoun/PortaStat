import os
try:
    from smbus2 import SMBus
except ImportError:
    if os.name == 'nt':  # Check if the operating system is Windows
        print("smbus2 library is not supported on Windows, using dummy class instead...")
        class SMBus:
            def __init__(self, *args, **kwargs):
                pass
            def read_i2c_block_data(self, *args, **kwargs):
                return [0x00] * 2  # most registers in this are 2 bytes wide
            def write_byte(self, address, value):
                pass
    else:
        raise ValueError("smbus2 library is not installed")


class I2C:
    """
    Wrapper class for smbus
    provide simple I²C transactions.
    """
    def __init__(self, bus_no=1):
        self.bus = SMBus(bus_no)

    def write_byte(self, address, value):
        self.bus.write_byte(address, value)

    def read_i2c_block_data(self, address, command, length):
        return self.bus.read_i2c_block_data(address, command, length)

    def scan(self):
        devices = list()
        # I2C addresses range from 1 to 127.
        for address in range(1, 128):
            try:
                self.bus.read_byte(address)
                devices.append(address)
            except Exception:
                pass
        return devices


class ADC081C021:
    """
    Library for the ADC081C021 8-Bit I²C-Compatible ADC with Alert Function.

    This class supports reading the conversion result, other functionality was ommited for simplicity.

    The device uses a pointer register system to select which internal register is accessed.
    The register pointer codes are defined below:

        0x00  Conversion Result (read only)
        0x01  Alert Status (read/write)
        0x02  Configuration (read/write)
        0x03  VLOW Limit (read/write, under-range alert threshold)
        0x04  VHIGH Limit (read/write, over-range alert threshold)
        0x05  VHYST (read/write, alert hysteresis)
        0x06  VMIN (Lowest Conversion, read/write in automatic mode)
        0x07  VMAX (Highest Conversion, read/write in automatic mode)

    Note that the conversion result is stored in a 16-bit register but only bits [11:4] contain the 8-bit ADC result.
    """
    # Pointer register addresses
    POINTER_CONVERSION    = 0x00
    POINTER_ALERT_STATUS  = 0x01
    POINTER_CONFIGURATION = 0x02
    POINTER_VLOW          = 0x03
    POINTER_VHIGH         = 0x04
    POINTER_VHYST         = 0x05
    POINTER_VMIN          = 0x06
    POINTER_VMAX          = 0x07

    def __init__(self, address=0x50, bus_no=1, vref=3.3):
        """
        ADC081C021 class for measuring battery voltage

        :param address: I²C 7-bit slave address (default is 0x50; for the ADC081C021 in SOT-6 the address is fixed)
        :param bus_no: I²C bus number (default is 1)
        :param vref: Reference voltage (VA) in volts. The ADC uses VA as the reference (default is 3.3 V)
        """
        self.address = address
        self.vref = vref
        self.i2c = I2C(bus_no)

    def _set_pointer(self, pointer):
        """
        Set the ADC's internal pointer register.

        :param pointer: Pointer code (0x00 to 0x07)
        """
        self.i2c.write_byte(self.address, pointer)

    def _read_bytes(self, pointer, length):
        """
        Read a block of bytes from an internal register specified by the pointer.

        :param pointer: Pointer register code to read from
        :param length: Number of bytes to read
        :return: List of read bytes
        """
        self._set_pointer(pointer)
        return self.i2c.read_i2c_block_data(self.address, pointer, length)

    def read_conversion_result(self):
        """
        Read the 16-bit conversion result from the ADC.

        The conversion result register (pointer 0x00) holds a 16-bit word where bits [11:4]
        represent the 8-bit digital conversion result

        :return: ADC conversion result as an integer between 0 and 255
        """
        data = self._read_bytes(self.POINTER_CONVERSION, 2)
        raw = (data[0] << 8) | data[1] # combine two 8 bit #'s into one 16 bit #
        result = (raw >> 4) & 0xFF # extract bits [11:4] (8-bit result)
        return result

    def read_voltage(self):
        """
        Convert the ADC's raw conversion result to a voltage.

        Since the ADC uses VA as its reference, the voltage is calculated as:
        
            voltage = (raw / 255) * VA

        :return: The measured analog voltage.
        """
        raw = self.read_conversion_result()
        voltage = (raw / 255.0) * self.vref
        return voltage

# Example usage:
if __name__ == '__main__':
    # Instantiate the ADC library (default address 0x50, I2C bus 1, Vref = 3.3V)
    adc = ADC081C021()
    # Read the raw conversion result and computed voltage
    voltage = adc.read_voltage()
    
    print("Measured Voltage: {:.3f} V".format(voltage))