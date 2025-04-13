import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import os

from Functions.eis import fit_eis_data, export_to_usb, run_demo_EIS_experiment, calibrate_all, set_output_amplitude, conduct_experiment
from Libraries.MUX_and_CLK_Library import Relays, LTC6904
from Libraries.AD5933_Library import AD5933

class EISWindow:
    def __init__(self, plot_frame, controls_frame, button_frame, toolbar_frame):
        self.plot_frame = plot_frame
        self.controls_frame = controls_frame
        self.button_frame = button_frame
        self.toolbar_frame = toolbar_frame
        self.root = toolbar_frame.winfo_toplevel()  # Get the root window

        # Initialize hardware first
        self.setup_hardware()

        # Configure grid weights for better layout
        self.plot_frame.grid_columnconfigure(0, weight=3)
        self.controls_frame.grid_columnconfigure(0, weight=1)

        # Configure frame grid with padding
        self.plot_frame.grid(padx=10, pady=10)
        self.controls_frame.grid(padx=10, pady=10)
        self.button_frame.grid(padx=10, pady=5)

        # Initialize variables
        self.spacing_type = ctk.StringVar(value="logarithmic")
        self.circuit_type = ctk.StringVar(value="Series RC")
        self.voltage = ctk.IntVar(value=1000)
        self.output_location = ctk.StringVar(value="100k")
        self.binary_search = ctk.BooleanVar(value=True)

        self.freq_data = None
        self.real_data = None
        self.imag_data = None
        self.phase_data = None
        self.freq_fit_data = None
        self.real_fit_data = None
        self.imag_fit_data = None

        # Setup UI components
        self.setup_ui()
        self.show_temp()

    def setup_ui(self):
        # Create main sections with titles
        self.create_section_label(self.controls_frame, "Experiment Settings", 0)
        self.setup_calibrate_and_voltage()
        self.setup_freq_and_spacing()

        self.create_section_label(self.controls_frame, "Analysis Settings", 4)
        self.setup_circuit_and_fitting()

        self.create_section_label(self.controls_frame, "Experiment Control", 7)
        self.setup_step_size_and_start()

        self.create_section_label(self.controls_frame, "Results", 9)
        self.setup_plot_and_params()
        self.setup_export_and_notification()

    def create_section_label(self, parent, text, row):
        label = ctk.CTkLabel(parent, text=text, font=("Helvetica", 14, "bold"))
        label.grid(row=row, column=0, pady=(15, 5), sticky="w")

    def setup_hardware(self):
        if os.name == 'nt':
            # Create dummy hardware for Windows testing
            class DummyHardware:
                def __init__(self):
                    self.sensor = type('DummySensor', (), {
                        'measure_temperature': lambda: 25,
                        'send_cmd': lambda x: None,
                        'set_output_voltage': lambda x: None
                    })()
                    self.Calibration_Mux = type('DummyMux', (), {'select_calibration': lambda x: None})()
                    self.Output_Gain_Mux = type('DummyMux', (), {'select_gain': lambda x: None})()
                    self.Input_Gain_Mux = type('DummyMux', (), {'select_gain': lambda x: None})()
                    self.CLK = type('DummyCLK', (), {'Turn_On_Clock': lambda x: None})()

            self.hardware = DummyHardware()
        else:
            self.hardware = self.HardwareComponents()

    class HardwareComponents:
        def __init__(self):
            self.sensor = AD5933()
            self.CLK = LTC6904()
            self.relays= Relays()
    '''
    def Temporary_Test(self):
        self.hardware.Calibration_Mux.select_calibration('100k')
        self.hardware.Electrode_Mux.select_electrode('3 Electrode')
        self.hardware.Output_Gain_Mux.select_gain('1x_uncorrected')
        self.hardware.Input_Gain_Mux.select_gain('10kx')
        self.hardware.sensor.set_output_voltage(1)

        #Calibration
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        num_steps = int(self.step_size_slider.get())
        spacing_type = self.spacing_type.get()
        self.send_notification("Calibrating EIS")
        self.hardware.sensor.Calibration_Sweep(100_000, min_freq, max_freq, num_steps, spacing_type=spacing_type)
        self.send_notification("Calibration Complete")

        #Run EIS
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        spacing_type = self.spacing_type.get()
        num_steps = int(self.step_size_slider.get())
        self.freq_data, self.real_data, self.imag_data, self.phase = self.hardware.sensor.Sweep_And_Adjust(min_freq, max_freq, num_steps, spacing_type=spacing_type)
        self.send_notification("Experiment Complete")
        self.update_plot()
    '''

    def show_temp(self):
        self.temperature = 25
        if os.name == 'nt':
            pass
        else:
            self.temperature = self.hardware.sensor.measure_temperature()
            self.hardware.sensor.send_cmd('STANDBY')

        # Create a frame for status indicators
        self.status_frame = ctk.CTkFrame(self.toolbar_frame)
        self.status_frame.pack(side=ctk.RIGHT, padx=10)

        # Temperature display
        temp_icon = ctk.CTkLabel(self.status_frame, text="🌡️", font=("Helvetica", 14))
        temp_icon.pack(side=ctk.LEFT, padx=(5,0))

        self.Temperature_Widget = ctk.CTkLabel(
            self.status_frame,
            text=f"{self.temperature}°C",
            font=("Helvetica", 12)
        )
        self.Temperature_Widget.pack(side=ctk.LEFT, padx=(0,5))

        # Separator
        separator = ctk.CTkLabel(self.status_frame, text="|", font=("Helvetica", 14))
        separator.pack(side=ctk.LEFT, padx=5)

        # Battery display
        self.battery_icon = ctk.CTkLabel(self.status_frame, text="🔋", font=("Helvetica", 14))
        self.battery_icon.pack(side=ctk.LEFT, padx=(5,0))

        self.battery_widget = ctk.CTkLabel(
            self.status_frame,
            text="100%",
            font=("Helvetica", 12)
        )
        self.battery_widget.pack(side=ctk.LEFT, padx=(0,5))

        # Start periodic battery update
        self.update_battery_level()

    def update_battery_level(self):
        if os.name == 'nt':
            # Dummy battery level for Windows testing
            battery_level = 85
        else:
            try:
                # Read battery level from system
                with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                    battery_level = int(f.read().strip())
            except:
                # Fallback if battery info is not available
                battery_level = -1

        # Update battery icon and text based on level
        if battery_level >= 0:
            # Update icon based on battery level
            if battery_level <= 20:
                self.battery_icon.configure(text="🪫")  # Low battery icon
            else:
                self.battery_icon.configure(text="🔋")  # Normal battery icon

            self.battery_widget.configure(text=f"{battery_level}%")
        else:
            self.battery_widget.configure(text="N/A")

        # Schedule next update in 30 seconds using the root window
        self.root.after(30000, self.update_battery_level)

    def setup_plot(self):
        matplotlib.rcParams['font.size'] = 10
        matplotlib.rcParams['figure.facecolor'] = '#2b2b2b'
        matplotlib.rcParams['axes.facecolor'] = '#2b2b2b'
        matplotlib.rcParams['axes.edgecolor'] = '#ffffff'
        matplotlib.rcParams['axes.labelcolor'] = '#ffffff'
        matplotlib.rcParams['xtick.color'] = '#ffffff'
        matplotlib.rcParams['ytick.color'] = '#ffffff'

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.figure.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    def setup_calibrate_and_voltage(self):
        self.calibrate_voltage_frame = ctk.CTkFrame(self.controls_frame)
        self.calibrate_voltage_frame.grid(row=1, column=0, pady=(0, 10), padx=5, sticky="ew")

        self.calibrate_button = ctk.CTkButton(
            self.calibrate_voltage_frame, 
            text="Calibrate EIS",
            command=self.calibrate_experiment,
            font=("Helvetica", 12)
        )
        self.calibrate_button.pack(side=ctk.LEFT, pady=3, padx=5)

        self.voltage_label = ctk.CTkLabel(self.calibrate_voltage_frame, text="Voltage (mV):", font=("Helvetica", 12))
        self.voltage_label.pack(side=ctk.LEFT, padx=5)

        voltage_values = ["2", "4", "10", "20", "38", "100", "200", "380", "1000", "2000"]
        self.voltage_dropdown = ctk.CTkComboBox(
            self.calibrate_voltage_frame,
            variable=self.voltage,
            values=voltage_values,
            command=self.update_voltage,
            font=("Helvetica", 12)
        )
        self.voltage_dropdown.pack(side=ctk.LEFT, padx=5)

        #self.Temporary_Test_Button = ctk.CTkButton(self.calibrate_voltage_frame, text="Temporary Test", command=self.Temporary_Test)
        #self.Temporary_Test_Button.pack(side=ctk.LEFT, pady=3, padx=10)

    def setup_freq_and_spacing(self):
        self.freq_frame = ctk.CTkFrame(self.controls_frame)
        self.freq_frame.grid(row=2, column=0, pady=(0, 10), padx=5, sticky="ew")

        # Min Frequency with improved styling
        self.min_freq_frame = ctk.CTkFrame(self.freq_frame)
        self.min_freq_frame.pack(fill=ctk.X, pady=2)
        self.min_freq_label = ctk.CTkLabel(self.min_freq_frame, text="Min Frequency:", font=("Helvetica", 12))
        self.min_freq_label.pack(side=ctk.LEFT, padx=5)
        self.min_freq_slider = ctk.CTkSlider(
            self.min_freq_frame,
            from_=10,
            to=20000,
            command=self.update_min_freq_label,
            number_of_steps=100
        )
        self.min_freq_slider.set(1000)
        self.min_freq_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.min_freq_value_label = ctk.CTkLabel(self.min_freq_frame, text=f"{self.min_freq_slider.get()}", width=50)
        self.min_freq_value_label.pack(side=ctk.LEFT, padx=2)

        # Max Frequency
        self.max_freq_frame = ctk.CTkFrame(self.freq_frame)
        self.max_freq_frame.pack(fill=ctk.X, pady=2)
        self.max_freq_label = ctk.CTkLabel(self.max_freq_frame, text="Max Frequency:", font=("Helvetica", 12))
        self.max_freq_label.pack(side=ctk.LEFT, padx=5)
        self.max_freq_slider = ctk.CTkSlider(self.max_freq_frame, from_=50000, to=200000, command=self.update_max_freq_label)
        self.max_freq_slider.set(100000)
        self.max_freq_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.max_freq_value_label = ctk.CTkLabel(self.max_freq_frame, text=f"{self.max_freq_slider.get()}", width=50)
        self.max_freq_value_label.pack(side=ctk.LEFT, padx=2)

        # Step Size
        self.step_size_frame = ctk.CTkFrame(self.freq_frame)
        self.step_size_frame.pack(fill=ctk.X, pady=2)
        self.step_size_label = ctk.CTkLabel(self.step_size_frame, text="Number Of Steps:", font=("Helvetica", 12))
        self.step_size_label.pack(side=ctk.LEFT, padx=5)
        self.step_size_slider = ctk.CTkSlider(self.step_size_frame, from_=1, to=2000, command=self.update_step_size_label)
        self.step_size_slider.set(100)
        self.step_size_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.step_size_value_label = ctk.CTkLabel(self.step_size_frame, text=f"{self.step_size_slider.get()}", width=50)
        self.step_size_value_label.pack(side=ctk.LEFT, padx=2)

        # Estimated Impedance
        self.impedance_frame = ctk.CTkFrame(self.freq_frame)
        self.impedance_frame.pack(fill=ctk.X, pady=2)
        self.impedance_label = ctk.CTkLabel(self.impedance_frame, text="Estimated Impedance:", font=("Helvetica", 12))
        self.impedance_label.pack(side=ctk.LEFT, padx=5)
        self.impedance_slider = ctk.CTkSlider(self.impedance_frame, from_=0, to=4, command=self.update_impedance_label)
        self.impedance_slider.set(0)
        self.impedance_slider.pack(side=ctk.LEFT, padx=5, fill=ctk.X, expand=True)
        self.impedance_value_label = ctk.CTkLabel(self.impedance_frame, text='100', width=50)
        self.impedance_value_label.pack(side=ctk.LEFT, padx=2)

        # Spacing Type
        self.spacing_type_frame = ctk.CTkFrame(self.controls_frame)
        self.spacing_type_frame.grid(row=3, column=0, pady=(0, 10), padx=5, sticky="ew")

        spacing_type_label = ctk.CTkLabel(self.spacing_type_frame, text="Frequency Spacing:", font=("Helvetica", 12))
        spacing_type_label.pack(side=ctk.LEFT, padx=10)

        self.logarithmic_radio = ctk.CTkRadioButton(
            self.spacing_type_frame,
            text="Logarithmic",
            variable=self.spacing_type,
            value="logarithmic",
            font=("Helvetica", 12)
        )
        self.logarithmic_radio.pack(side=ctk.LEFT, padx=10)

        self.linear_radio = ctk.CTkRadioButton(
            self.spacing_type_frame,
            text="Linear",
            variable=self.spacing_type,
            value="linear",
            font=("Helvetica", 12)
        )
        self.linear_radio.pack(side=ctk.LEFT, padx=10)

    def update_min_freq_label(self, value):
        step_value = round(float(value) / 100) * 100
        self.min_freq_value_label.configure(text=f"{step_value}")
        self.min_freq_slider.set(step_value)

    def update_max_freq_label(self, value):
        step_value = round(float(value) / 1000) * 1000
        self.max_freq_value_label.configure(text=f"{step_value}")
        self.max_freq_slider.set(step_value)

    def update_step_size_label(self, value):
        step_value = round(float(value) / 10) * 10
        self.step_size_value_label.configure(text=f"{step_value}")
        self.step_size_slider.set(step_value)

    def update_impedance_label(self, value):
        impedance_values = {0: '100', 1: '10k', 2: '100k', 3: '1Meg', 4: '10Meg'}
        step_value = int(value)
        self.impedance_value_label.configure(text=impedance_values[step_value])
        self.impedance_slider.set(step_value)

    def setup_step_size_and_start(self):
        self.start_fitting_frame = ctk.CTkFrame(self.controls_frame)
        self.start_fitting_frame.grid(row=8, column=0, pady=(0, 10), padx=5, sticky="ew")

        # Create a frame for experiment settings
        settings_frame = ctk.CTkFrame(self.start_fitting_frame)
        settings_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5, pady=3)

        # Output location selection
        output_frame = ctk.CTkFrame(settings_frame)
        output_frame.pack(fill=ctk.X, padx=5, pady=2)

        output_label = ctk.CTkLabel(output_frame, text="Output Location:", font=("Helvetica", 12))
        output_label.pack(side=ctk.LEFT, padx=5)

        locations = ['Counter0', 'Counter1', 'Randles', '100', '10k', '100k', '1Meg', '10Meg']
        self.output_location_dropdown = ctk.CTkComboBox(
            output_frame,
            variable=self.output_location,
            values=locations,
            font=("Helvetica", 12),
            width=120
        )
        self.output_location_dropdown.pack(side=ctk.LEFT, padx=5)

        # Auto gain checkbox
        gain_frame = ctk.CTkFrame(settings_frame)
        gain_frame.pack(fill=ctk.X, padx=5, pady=2)

        self.binary_search_checkbox = ctk.CTkCheckBox(
            gain_frame,
            variable=self.binary_search,
            text="Auto Gain",
            font=("Helvetica", 12)
        )
        self.binary_search_checkbox.pack(side=ctk.LEFT, padx=5)

        # Start button with progress indicator
        button_frame = ctk.CTkFrame(self.start_fitting_frame)
        button_frame.pack(side=ctk.RIGHT, fill=ctk.Y, padx=5, pady=3)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start EIS",
            command=self.start_experiment,
            font=("Helvetica", 12, "bold"),
            width=120,
            height=50
        )
        self.start_button.pack(pady=3)

    def setup_circuit_and_fitting(self):
        self.circuit_type_frame = ctk.CTkFrame(self.controls_frame)
        self.circuit_type_frame.grid(row=5, column=0, pady=(0, 10), padx=5, sticky="ew")

        self.left_frame = ctk.CTkFrame(self.circuit_type_frame)
        self.left_frame.pack(side=ctk.LEFT, pady=3, padx=5)

        circuit_label = ctk.CTkLabel(self.left_frame, text="Circuit Model:", font=("Helvetica", 12))
        circuit_label.pack(pady=(3,0), padx=5)

        self.circuit_type_dropdown = ctk.CTkComboBox(
            self.left_frame,
            variable=self.circuit_type,
            values=["Series RC", "Parallel RC", "Randles", "Randles With CPE"],
            font=("Helvetica", 12)
        )
        self.circuit_type_dropdown.pack(pady=3, padx=5)

        self.run_fitting_button = ctk.CTkButton(
            self.left_frame,
            text="Run Fitting",
            command=self.run_fitting,
            font=("Helvetica", 12)
        )
        self.run_fitting_button.pack(pady=3, padx=5, fill=ctk.X)

        # Parameters display with title
        params_frame = ctk.CTkFrame(self.circuit_type_frame)
        params_frame.pack(side=ctk.LEFT, pady=2, padx=5, fill=ctk.BOTH, expand=True)

        params_label = ctk.CTkLabel(params_frame, text="Fitted Parameters:", font=("Helvetica", 12))
        params_label.pack(pady=(3,0), padx=5)

        self.params_display = ctk.CTkTextbox(params_frame, height=80, width=250)
        self.params_display.pack(pady=(0,3), padx=5, fill=ctk.BOTH, expand=True)
        self.params_display.configure(state="disabled")

    def setup_plot_and_params(self):
        self.plot_type = ctk.StringVar(value="mag_vs_freq")

        # Create a frame for plot controls with a title
        plot_controls_frame = ctk.CTkFrame(self.button_frame)
        plot_controls_frame.pack(fill=ctk.X, padx=10, pady=5)

        plot_label = ctk.CTkLabel(plot_controls_frame, text="Plot Type:", font=("Helvetica", 12, "bold"))
        plot_label.pack(side=ctk.LEFT, padx=(10,20))

        # Organize radio buttons in a more compact way
        radio_buttons = [
            ("Magnitude vs Frequency", "mag_vs_freq"),
            ("Phase vs Frequency", "phase_vs_freq"),
            ("Imaginary vs Real", "imag_vs_real"),
            ("Real vs Frequency", "real_vs_freq"),
            ("Imaginary vs Frequency", "imag_vs_freq")
        ]

        for text, value in radio_buttons:
            btn = ctk.CTkRadioButton(
                plot_controls_frame,
                text=text,
                variable=self.plot_type,
                value=value,
                command=self.update_plot,
                font=("Helvetica", 12)
            )
            btn.pack(side=ctk.LEFT, padx=10)

        self.setup_plot()

    def setup_export_and_notification(self):
        self.export_frame = ctk.CTkFrame(self.controls_frame)
        self.export_frame.grid(row=10, column=0, pady=(0, 10), padx=5, sticky="ew")

        # Export controls
        export_controls = ctk.CTkFrame(self.export_frame)
        export_controls.pack(side=ctk.LEFT, pady=3, padx=5, fill=ctk.Y)

        self.export_button = ctk.CTkButton(
            export_controls,
            text="Export Data",
            command=self.export_data,
            font=("Helvetica", 12)
        )
        self.export_button.pack(pady=3, padx=5)

        # Notification area with title
        notification_frame = ctk.CTkFrame(self.export_frame)
        notification_frame.pack(side=ctk.LEFT, pady=3, padx=5, fill=ctk.BOTH, expand=True)

        notification_label = ctk.CTkLabel(notification_frame, text="Status Messages:", font=("Helvetica", 12))
        notification_label.pack(pady=(3,0), padx=5, anchor="w")

        self.notification_box = ctk.CTkTextbox(notification_frame, height=80, width=275)
        self.notification_box.pack(pady=(0,3), padx=5, fill=ctk.BOTH, expand=True)
        self.notification_box.insert(ctk.END, "Welcome! Please calibrate your device.")
        self.notification_box.configure(state="disabled")

    def send_notification(self, message, newline=True):
        if newline:
            message = "\n" + message
        self.notification_box.configure(state="normal")
        self.notification_box.insert(ctk.END, message)
        self.notification_box.see(ctk.END)
        self.notification_box.configure(state="disabled")

        # Automatically clear old messages if too many
        content = self.notification_box.get("1.0", ctk.END)
        lines = content.split('\n')
        if len(lines) > 10:  # Keep only last 10 messages
            self.notification_box.configure(state="normal")
            self.notification_box.delete("1.0", f"{len(lines)-10}.0")
            self.notification_box.configure(state="disabled")

    # External Calls
    def export_data(self):
        # make sure there is actually data to export
        if self.freq_data is None:
            self.send_notification("No data to export. Please run an experiment first.")
        else:
            export_to_usb(self.send_notification, self.freq_data, self.real_data, self.imag_data)

    def update_voltage(self, why):
        set_output_amplitude(self.voltage.get(), self.hardware.sensor, self.hardware.relays, self.send_notification)

    # Experiments
    def calibrate_experiment(self):
        max_freq = int(self.max_freq_slider.get())
        min_freq = int(self.min_freq_slider.get())
        spacing_type = self.spacing_type.get()
        num_steps = int(self.step_size_slider.get())
        voltage = self.voltage.get()
        calibrate_all(voltage, min_freq, max_freq, self.hardware, self.send_notification, num_steps, spacing_type)

    def start_experiment(self):
        # Disable controls during experiment
        self.start_button.configure(state="disabled", text="Running...")
        self.output_location_dropdown.configure(state="disabled")
        self.binary_search_checkbox.configure(state="disabled")

        try:
            if os.name == 'nt':
                run_demo_EIS_experiment(
                    self.update_data,
                    int(self.min_freq_slider.get()),
                    int(self.max_freq_slider.get()),
                    self.spacing_type.get(),
                    int(self.step_size_slider.get())
                )
                self.send_notification("Demo Experiment Complete")
            else:
                max_freq = int(self.max_freq_slider.get())
                min_freq = int(self.min_freq_slider.get())
                spacing_type = self.spacing_type.get()
                num_steps = int(self.step_size_slider.get())
                voltage = self.voltage.get()
                estimated_impedance = self.impedance_slider.get()
                output_location = self.output_location.get()
                binary_search = self.binary_search.get()
                
                self.freq_data, self.real_data, self.imag_data, self.phase = conduct_experiment(
                    self.hardware,
                    self.send_notification,
                    voltage,
                    estimated_impedance,
                    min_freq,
                    max_freq,
                    num_steps,
                    spacing_type,
                    output_location,
                    binary_search
                )
                self.update_plot()
        finally:
            # Re-enable controls after experiment
            self.start_button.configure(state="normal", text="Start EIS")
            self.output_location_dropdown.configure(state="normal")
            self.binary_search_checkbox.configure(state="normal")

    def run_fitting(self):
        circuit = self.circuit_type.get()
        real_fit, imag_fit, fitted_params, Labels = fit_eis_data(self.freq_data, self.real_data, self.imag_data, circuit)
        self.update_fit_data(real_fit, imag_fit, fitted_params, Labels)
        self.send_notification("Fitting Complete")

    # Update Data and Plots
    def update_data(self, freq_data, real_data, imag_data):
        self.freq_data = freq_data
        self.real_data = real_data
        self.imag_data = imag_data
        self.phase = np.rad2deg(np.arctan2(imag_data, real_data))
        self.update_plot()

    def update_fit_data(self, real_fit, imag_fit, fitted_params, Labels):
        self.freq_fit_data = self.freq_data
        self.real_fit_data = real_fit
        self.imag_fit_data = imag_fit
        self.params_display.delete(1.0, ctk.END)
        self.params_display.insert(ctk.END, f"Fitted Parameters:\n{Labels}\n{fitted_params}")
        self.update_plot()

    def update_plot(self):
        plot_type = self.plot_type.get()

        # Clear previous plot
        self.ax.clear()

        if not hasattr(self, 'freq_data') or self.freq_data is None:
            self.ax.text(0.5, 0.5, 'No data available\nRun an experiment first',
                        ha='center', va='center', transform=self.ax.transAxes,
                        color='white', fontsize=12)
            self.canvas.draw()
            return

        if plot_type == "mag_vs_freq":
            self.plot_freq_vs_mag()
        elif plot_type == "phase_vs_freq":
            self.plot_freq_vs_phase()
        elif plot_type == "imag_vs_real":
            self.plot_real_vs_imag()
        elif plot_type == "real_vs_freq":
            self.plot_freq_vs_real()
        elif plot_type == "imag_vs_freq":
            self.plot_freq_vs_imag()

    def plot_freq_vs_mag(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, np.sqrt(self.real_data**2 + self.imag_data**2), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.sqrt(self.real_fit_data**2 + self.imag_fit_data**2), color='red')
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Magnitude")
        self.ax.set_title("Magnitude vs Frequency")
        self.canvas.draw()

    def plot_freq_vs_phase(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, self.phase, s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, np.rad2deg(np.arctan2(self.imag_fit_data, self.real_fit_data)), color='red')
        self.ax.set_xscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Phase")
        self.ax.set_title("Phase vs Frequency")
        self.canvas.draw()

    def plot_real_vs_imag(self):
        self.ax.clear()
        self.ax.scatter(self.real_data, -self.imag_data, s=5)
        if self.real_fit_data is not None:
            self.ax.plot(self.real_fit_data, -self.imag_fit_data, color='red')
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")
        self.ax.set_title("Imaginary vs Real")
        self.canvas.draw()

    def plot_freq_vs_real(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, abs(self.real_data), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, abs(self.real_fit_data), color='red')
        self.ax.set_xscale("log")
        self.ax.set_yscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Real")
        self.ax.set_title("Real vs Frequency")
        self.canvas.draw()

    def plot_freq_vs_imag(self):
        self.ax.clear()
        self.ax.scatter(self.freq_data, abs(self.imag_data), s=5)
        if self.freq_fit_data is not None:
            self.ax.plot(self.freq_fit_data, abs(self.imag_fit_data), color='red')
        self.ax.set_xscale("log")
        self.ax.set_yscale("log")
        self.ax.set_xlabel("Frequency")
        self.ax.set_ylabel("Imaginary")
        self.ax.set_title("Imaginary vs Frequency")
        self.canvas.draw()

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            if widget.winfo_children():
                self.clear_frame(widget)
            widget.destroy()

    def destroy(self):
        self.ax.clear()
        self.canvas.get_tk_widget().pack_forget()
        self.canvas.get_tk_widget().destroy()
        self.clear_frame(self.controls_frame)
        self.clear_frame(self.button_frame)
        self.clear_frame(self.plot_frame)
        if hasattr(self, 'status_frame'):
            self.status_frame.destroy()
