import numpy as np
import impedance as imp
from impedance.models.circuits import CustomCircuit
import csv
import os
import time
import psutil
import re

def calculate_impedance(frequencies, Rs, Rp, C):
    omega = 2 * np.pi * frequencies
    Z_R = Rs
    Z_C = Rp / (1 + Rp * 1j * omega * C)
    Z = Z_R + Z_C
    return Z.real, Z.imag

def run_demo_EIS_experiment(update_data_callback, max_freq, min_freq, spacing_type, num_steps):
    if spacing_type == 'logarithmic':
        frequencies = np.logspace(np.log10(min_freq), np.log10(max_freq), num = num_steps)
    else:
        frequencies = np.linspace(min_freq, max_freq, num_steps)
    
    Rs = 10000
    Rp = 100000
    C = 5E-9
    
    real_impedances, imag_impedances = calculate_impedance(frequencies, Rs, Rp, C)

    update_data_callback(frequencies, real_impedances, imag_impedances)

def extract_information(input_string):
    # Extract the relevant information using regular expressions
    pattern = r'(?:R|C|CPE|Wo)\d+|(?<=,)(?:R|C|CPE|Wo)\d+(?=\))'
    extracted_info = re.findall(pattern, input_string)
    for i, item in enumerate(extracted_info):
        if 'CPE' in item:
            num = item[3:]
            extracted_info[i] = 'Q' + num
            extracted_info.insert(i+1, 'n' + num)
    return extracted_info

def fit_eis_data(frequencies, real_impedances, imag_impedances, circuit):
    Z = real_impedances + 1j * imag_impedances

    # Define circuit models
    if circuit == 'Series RC':
        circuit_model = 'R0-C1'
        initial_guess = [100000, 1e-9]
    elif circuit == 'Parallel RC':
        circuit_model = 'p(R0, C1)'
        initial_guess = [100000, 1e-9]
    elif circuit == 'Randles':
        circuit_model = 'R0-p(C1,R1)'
        initial_guess = [10000, 1e-9, 100000]
    elif circuit == 'Randles With CPE':
        circuit_model = 'R0-p(CPE1,R1)'
        initial_guess = [10000, 1e-9, 0.9, 100000]
    else:
        raise ValueError(f"Unknown circuit type: {circuit}")
    circuit = CustomCircuit(initial_guess=initial_guess, circuit=circuit_model)
    circuit.fit(frequencies, Z)

    fitted_params = circuit.parameters_
    Z_fit = circuit.predict(frequencies)
    real_fit = Z_fit.real
    imag_fit = Z_fit.imag

    print(f"Fitted parameters: {fitted_params}")
    return real_fit, imag_fit, fitted_params, extract_information(circuit_model)

def detect_usb_drive():
    """Detect the USB drive mount point."""
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if 'media' in partition.mountpoint and 'rw' in partition.opts:  # 'rw' indicates read/write access
            return partition.mountpoint
    return None

def export_to_usb(send_notification, frequencies, real, imaginary):
    """Export frequencies, real, and imaginary data to a CSV file on a USB drive."""
    usb_mount_point = None
    # Wait until a USB drive is detected
    send_notification("Waiting for USB drive...")
    while usb_mount_point is None:
        usb_mount_point = detect_usb_drive()
        if usb_mount_point is None:
            time.sleep(1)  # Check every second

    # Prepare the file path
    file_path = os.path.join(usb_mount_point, 'exported_data.csv')
    
    # Write data to CSV file
    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Frequency', 'Real', 'Imaginary'])
            for f, r, i in zip(frequencies, real, imaginary):
                writer.writerow([f, str(r), str(i)])
        send_notification(f"Data successfully exported to {file_path}")
    except Exception as e:
        send_notification(f"Failed to write to CSV: {e}")

def set_output_amplitude(voltage, sensor, relays, send_notification):
    if voltage == "2mV" or voltage == '2' or voltage == 2:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('.01x')
    elif voltage == "4mV" or voltage == '4' or voltage == 4:
        sensor.set_output_voltage(.4)
        relays.set_output_gain('.01x')
    elif voltage == "10mV" or voltage == '10' or voltage == 10:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('.05x')
    elif voltage == "20mV" or voltage == '20' or voltage == 20:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('.1x')
    elif voltage == "40mV" or voltage == '40' or voltage == 40:
        sensor.set_output_voltage(.4)
        relays.set_output_gain('.1x')
    elif voltage == "50mV" or voltage == '50' or voltage == 50:
        sensor.set_output_voltage(1)
        relays.set_output_gain('.05x')
    elif voltage == "100mV" or voltage == '100' or voltage == 100:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('.5x')
    elif voltage == "150mV" or voltage == '150' or voltage == 150:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('.75x')
    elif voltage == "200mV" or voltage == '200' or voltage == 200:
        sensor.set_output_voltage(.2)
        relays.set_output_gain('1x')
    elif voltage == "300mV" or voltage == '300' or voltage == 300:
        sensor.set_output_voltage(.4)
        relays.set_output_gain('.75x')
    elif voltage == "400mV" or voltage == '400' or voltage == 400:
        sensor.set_output_voltage(.4)
        relays.set_output_gain('1x')
    elif voltage == "500mV" or voltage == '500' or voltage == 500:
        sensor.set_output_voltage(1)
        relays.set_output_gain('.5x')
    elif voltage == "750mV" or voltage == '750' or voltage == 750:
        sensor.set_output_voltage(1)
        relays.set_output_gain('.75x')
    elif voltage == "1V" or voltage == '1000' or voltage == 1000:
        sensor.set_output_voltage(1)
        relays.set_output_gain('1x')
    elif voltage == "1.5V" or voltage == '1500' or voltage == 1500:
        sensor.set_output_voltage(2)
        relays.set_output_gain('.75x')
    elif voltage == "2V" or voltage == '2000' or voltage == 2000:
        sensor.set_output_voltage(2)
        relays.set_output_gain('1x')
    else:
        send_notification("Invalid voltage value")


def Adjust_Magnitude_Return_abs_Impedance(Freqs_Measured, real, imag, Freqs_Calibration, GainFactors):
    if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
        raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
    Magnitudes_Measured = np.sqrt(real**2 + imag**2)
    interpolated_gain_factors = np.interp(Freqs_Measured, Freqs_Calibration, GainFactors)
    adjusted_magnitudes = [mag * gf for mag, gf in zip(Magnitudes_Measured, interpolated_gain_factors)]
    adjusted_impedances = [1/mag for mag in adjusted_magnitudes]
    return adjusted_impedances

def Adjust_Phase_Return_Phase(Freqs_Measured, real_list, imag_list, Freqs_Calibration, Sys_Phases):
    if any(f < min(Freqs_Calibration) or f > max(Freqs_Calibration) for f in Freqs_Measured):
        raise ValueError("One or more measured frequencies fall outside the calibration frequency range.")
    Phases_Measured = find_phase_arctan_vectorized(real_list, imag_list)
    interpolated_sys_phases = np.interp(Freqs_Measured, Freqs_Calibration, Sys_Phases)
    adjusted_phases = [phase - sys_phase for phase, sys_phase in zip(Phases_Measured, interpolated_sys_phases)]
    return adjusted_phases

def Adjust_Magnitude_Return_abs_Impedance_single(Freq_Measured, real, imag, Freqs_Calibration, GainFactors):
    if Freq_Measured < min(Freqs_Calibration) or Freq_Measured > max(Freqs_Calibration):
        raise ValueError("The measured frequency falls outside the calibration frequency range.")
    Magnitude_Measured = np.sqrt(real**2 + imag**2)
    interpolated_gain_factor = np.interp(Freq_Measured, Freqs_Calibration, GainFactors)
    adjusted_magnitude = Magnitude_Measured * interpolated_gain_factor
    adjusted_impedance = 1 / adjusted_magnitude
    return adjusted_impedance

def Adjust_Phase_Return_Phase_single(Freq_Measured, real, imag, Freqs_Calibration, Sys_Phases):
    if Freq_Measured < min(Freqs_Calibration) or Freq_Measured > max(Freqs_Calibration):
        raise ValueError("The measured frequency falls outside the calibration frequency range.")
    Phase_Measured = find_phase_arctan(real, imag)
    interpolated_sys_phase = np.interp(Freq_Measured, Freqs_Calibration, Sys_Phases)
    adjusted_phase = Phase_Measured - interpolated_sys_phase
    return adjusted_phase

def find_phase_arctan_vectorized(real_list, imag_list):
    real_array = np.array(real_list)
    imag_array = np.array(imag_list)
    vectorized_find_phase_arctan = np.vectorize(find_phase_arctan)
    return vectorized_find_phase_arctan(real_array, imag_array)

def find_phase_arctan(real, imag):
    if real > 0 and imag > 0:
        return (np.arctan(imag/real))*(180/np.pi)
    elif real < 0 and imag > 0:
        return 180 + (np.arctan(imag/real))*(180/np.pi)
    elif real < 0 and imag < 0:
        return 180 + (np.arctan(imag/real))*(180/np.pi)
    elif real > 0 and imag < 0:
        return 360 + (np.arctan(imag/real))*(180/np.pi)
    else:
        ValueError('Invalid Input')



def calibrate_all(voltage, start_freq, end_freq, hardware, send_notification, num_steps, spacing_type, progress_bar=None):
    """
    Calibrate all input gain factors
    """

    ## run
    send_notification('Calibrating...')
    send_notification(str(voltage))
    set_output_amplitude(voltage, hardware.sensor, hardware.relays, send_notification)

    impedances = [10e6, 1e6, 500e3, 100e3, 50e3, 10e3, 1e3, 100]
    gains_and_gainfactors = [(10,2), (10,5), (100,2), (100,5), (1e3,2), (1e3,5), (10e3,2), (10e3,5), (100e3,2), (100e3,5), (1e6,2), (1e6,5)]
    gains_len = len(gains_and_gainfactors)
    tot_len = len(impedances)*gains_len

    for i, impedance in enumerate(impedances):
        hardware.relays.select_calibration(impedance)
        
        estimated_current = (voltage/1000)/impedance
        estimated_gain = None

        for j, gains_and_gainfactor in enumerate(gains_and_gainfactors):
            gain, gain_factor = gains_and_gainfactor

            if _VCC_railing(gain_factor, estimated_current, gain):  #~~VCC/2
                progress_ind = i*gains_len + (j+1)
                progress_bar.set( (progress_ind/tot_len) *100)
                estimated_gain = gain
            else:
                progress_ind = i*gains_len + gains_len
                progress_bar.set( (progress_ind/tot_len) *100)
                break
        if estimated_gain is None:
            send_notification("Unable to find suitable gain setting")
        hardware.relays.set_input_gain(estimated_gain)

        
        freqs, GainFactors, Sys_Phases = hardware.sensor.Calibration_Sweep(impedance, start_freq, end_freq, num_steps, hardware, spacing_type)


        export_calibration_data(freqs, GainFactors, Sys_Phases, voltage, int(impedance))

        send_notification(impedance, newline=False)
    send_notification("Calibration complete")

def _VCC_railing(gain_factor, estimated_current, gain):
    """
    Returns truth of vcc railing
    """
    if gain_factor == 2:
        vcc_railing = estimated_current * gain * 2 < 1.4 #~~VCC/2
    elif gain_factor == 5:
        vcc_railing = estimated_current * gain * 5 < 1.5 #~~VCC/2
    return vcc_railing


def conduct_experiment(hardware, send_notification, voltage, estimated_impedance, start_freq, end_freq, num_steps = 100, spacing_type='logarithmic', output_location = 'Counter', binary_search = True, progress_bar=None):
    
    send_notification("Running EIS experiment...")

    #Set Calibration
    hardware.relays.select_calibration(output_location)

    #Set Output
    set_output_amplitude(voltage, hardware.sensor, hardware.relays, send_notification)
    #Set Gain
    impedance_values = {0: '10', 1: '100', 2: '1000', 3: '10000', 4: '100000', 5: '1000000'}
    estimated_impedance = int(impedance_values[estimated_impedance])

    if binary_search == True:
        freqs, real, imag, Phase = conduct_binary_search_experiment(hardware, send_notification, voltage, estimated_impedance, start_freq, end_freq, num_steps, spacing_type, progress_bar)
        
    else:
        estimated_gain = find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification)
        hardware.relays.set_input_gain(estimated_gain)
        #Run Experiment
        freqs, real, imag = hardware.sensor.Complete_Sweep(start_freq, end_freq, num_steps, hardware, spacing_type)

        #Adjust Data
        cal_data = import_calibration_data(voltage, estimated_impedance)
        Magnitude = Adjust_Magnitude_Return_abs_Impedance(freqs, real, imag, cal_data.Cal_Freqs, cal_data.Gain_Factors)
        Phase = Adjust_Phase_Return_Phase(freqs, real, imag, cal_data.Cal_Freqs, cal_data.Sys_Phases)
        freqs = np.array(freqs)
        Magnitude = np.array(Magnitude)
        Phase = np.array(Phase)
        real = Magnitude * np.cos(np.deg2rad(Phase))
        imag = Magnitude * np.sin(np.deg2rad(Phase))

    return freqs, real, imag, Phase

def binary_search_gain(hardware, send_notification, voltage, estimated_impedance, freq, calibration_data):
    for trial in range(3):
        # Setup starting parameters
        estimated_gain = find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification)
        hardware.relays.set_input_gain(estimated_gain)
        real_temp, imag_temp = hardware.sensor.run_freq_sweep(freq)
    
        # Adjust the impedance with the calibration factor
        estimated_impedance = find_impedance_from_voltage_and_gain(voltage, estimated_gain, send_notification)
        impedance = Adjust_Magnitude_Return_abs_Impedance_single(
            freq, real_temp, imag_temp, 
            calibration_data[str(estimated_impedance)].Cal_Freqs, 
            calibration_data[str(estimated_impedance)].Gain_Factors
        )
        optimal_gain = find_gain_from_voltage_and_Impedance(voltage, impedance, send_notification)
        if optimal_gain == estimated_gain:
            break
        else:
            estimated_gain = optimal_gain
    Phase = Adjust_Phase_Return_Phase_single(
        freq, real_temp, imag_temp, 
        calibration_data[str(estimated_impedance)].Cal_Freqs, 
        calibration_data[str(estimated_impedance)].Gain_Factors
    )
    real = impedance * np.cos(np.deg2rad(Phase))
    imag = impedance * np.sin(np.deg2rad(Phase))

    return impedance, real, imag, Phase

def conduct_binary_search_experiment(hardware, send_notification, voltage, impedance, start_freq, end_freq, num_steps, spacing_type, progress_bar):
    # Setup Frequencies of interest
    if spacing_type == 'logarithmic':
        freqs = np.logspace(np.log10(start_freq), np.log10(end_freq), num=num_steps)
    elif spacing_type == 'linear':
        freqs = np.linspace(start_freq, end_freq, num=num_steps)
    else:
        raise ValueError('Invalid Frequency Spacing Type')

    # Import Calibration Data
    calibration_data = import_all_calibration_data(voltage)
    
    # Initialize results arrays
    real_results = np.zeros(num_steps)
    imag_results = np.zeros(num_steps)
    phase_results = np.zeros(num_steps)

    # Repeat the first datapoint for settling
    for _ in range(5):
        real_temp, imag_temp = hardware.sensor.run_freq_sweep(freqs[0])

    # Loop through each frequency
    for i, freq in enumerate(freqs):
        progress_bar.set( ((i+1)/len(freqs)) *100)
        impedance, real_adjusted, imag_adjusted, Phase = binary_search_gain(
            hardware, send_notification, voltage, impedance, freq, calibration_data)
        real_results[i] = real_adjusted
        imag_results[i] = imag_adjusted
        phase_results[i] = Phase

    return freqs, real_results, imag_results, phase_results

def export_calibration_data(freqs, gain_factors, sys_phases, voltage, Impedance):
    data = np.array([freqs, gain_factors, sys_phases])
    folder_name = 'calibration_data'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    file_name = f'{voltage}_{Impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    np.savetxt(file_path, data, delimiter=',')

class CalibrationData:
    def __init__(self, cal_freqs, gain_factors, sys_phases):
        self.Cal_Freqs = cal_freqs
        self.Gain_Factors = gain_factors
        self.Sys_Phases = sys_phases

def import_calibration_data(voltage, impedance):
    folder_name = 'calibration_data'
    file_name = f'{voltage}_{impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    data = np.loadtxt(file_path, delimiter=',')
    return CalibrationData(data[0], data[1], data[2])

def import_all_calibration_data(voltage):
    calibration_data = {}
    for impedance in ['100', '1000', '10000', '50000', '100000', '500000', '1000000', '10000000']:
        calibration_data[impedance] = import_calibration_data(voltage, impedance)
    return calibration_data

def find_gain_from_voltage_and_Impedance(voltage, estimated_impedance, send_notification):
    estimated_current = (voltage/1000)/estimated_impedance
    estimated_gain = None
    gains_and_gainfactors = [(10,2), (10,5), (100,2), (100,5), (1e3,2), (1e3,5), (10e3,2), (10e3,5), (100e3,2), (100e3,5), (1e6,2), (1e6,5)]
    for i, gains_and_gainfactor in enumerate(gains_and_gainfactors):
        gain, gainfactor = gains_and_gainfactor
        if _VCC_railing(gainfactor, estimated_current, gain):
            estimated_gain = gain
        else:
            break
    if estimated_gain is None:
        send_notification("Unable to find suitable gain setting, Defaulting to 100k")
        return int(100e3)
    else:
        send_notification(f"Estimated input gain setting: {estimated_gain}")
        return int(estimated_gain)

def find_impedance_from_voltage_and_gain(voltage, gain, send_notification):
    estimate = (voltage / 1000) * gain * 5 / 1.5
    impedances = [100, 1e3, 10e3, 50e3, 100e3, 500e3, 1e6, 10e6]
    estimated_impedance = None
    
    for impedance in impedances:
        if estimate < impedance:
            break
        else:
            estimated_impedance = impedance
    
    if estimated_impedance is None:
        send_notification("Unable to find suitable impedance setting, Defaulting to 10k")
        return int(10e3)
    else:
        send_notification(f"Estimated impedance setting: {estimated_impedance}")
        return int(estimated_impedance)


def clk_adjustment(hardware, frequency):
    # 10k min frequency, 16M clk
    # scale clk by factor of 1600
    # assume factor of 1000 for a little higher range

    # LTC6904 min is 1khz -> 68khz
    # theoretical limit is .5hz
    sys_clk = frequency * 1000
    if sys_clk > 16.776e6:
        sys_clk = 16.776e6

    hardware.CLK.Turn_On_Clock(sys_clk)
    hardware.sensor.set_clk_variable(sys_clk)


'''
def import_calibration_data(voltage, impedance):
    folder_name = 'calibration_data'
    file_name = f'{voltage}_{impedance}.csv'
    file_path = os.path.join(folder_name, file_name)
    data = np.loadtxt(file_path, delimiter=',')
    return data[0], data[1], data[2]

def import_all_calibration_data(voltage):
    calibration_data = {}
    for impedance in ['10, '100', '10000', '100000', '1000000', '10000000']:
        calibration_data[impedance] = import_calibration_data(voltage, impedance)
    return calibration_data
'''


