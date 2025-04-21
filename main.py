import customtkinter as ctk
import os
from gui.eis_window import EISWindow
from gui.readme_window import ReadmeWindow


class MainApplication(ctk.CTk):
    """
    Main class used in event loop.

    This class handles the primary window setup and management of the
    application interface, including toolbar, frames, and window controls.

    Inherits from customtkinter.CTk.
    """
    def __init__(self):
        super().__init__()

        # Window setup w/built-in functionality
        self.title("Experiment GUI")
        # Set default geometry as fallback
        self.geometry("800x480")
        self._set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Set fullscreen mode
        self.fullscreen = os.name != 'nt'  # True if not on Windows
        if self.fullscreen:
            self.attributes('-fullscreen', True)
        
        # Bind Escape key to toggle fullscreen
        self.bind('<Escape>', self.toggle_fullscreen)
        
        # Custom variables
        self.current_window = None
        self.previous_selection = "EIS"

        # Custom functions
        self.setup_main_frame()
        self.setup_frames()
        self.on_selection_change("EIS")

    def toggle_fullscreen(self, event=None):
        if os.name != 'nt':  # Only on Raspberry Pi
            self.fullscreen = not self.fullscreen
            self.attributes('-fullscreen', self.fullscreen)
            if not self.fullscreen:
                self.geometry("800x480")

    def setup_main_frame(self):
        """Main frame is an empty widget to place all other widgets within"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        self.readme_text_area = None

    def setup_frames(self):
        # frame for open, close, & temp
        self.toolbar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.toolbar_frame.grid(row=0, column=0, sticky="ew")
        
        readme_button = ctk.CTkButton(self.toolbar_frame, text="Open README", command=self.open_readme, width=100)
        readme_button.pack(side=ctk.LEFT, padx=(2,10))

        self.temperature_widget = ctk.CTkLabel(self.toolbar_frame, text='25 °C')
        self.temperature_widget.pack(side=ctk.LEFT, padx=50)
        self.temperature_widget.configure(corner_radius=8)

        close_button = ctk.CTkButton(self.toolbar_frame, text="Close", command=self.on_close, width=100)
        close_button.pack(side=ctk.RIGHT, padx=(10,2), pady=2)

        # frame for plot
        self.plot_frame = ctk.CTkFrame(self.main_frame)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

        # frame for: experiment settings, analysis settings, experimental control, & results
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.grid(row=0, column=1, sticky="nsew", rowspan=2)

        # frame for plot types
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Configure grid weights
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=0)  # toolbar row
        self.main_frame.grid_rowconfigure(1, weight=1)  # plot row
        self.main_frame.grid_rowconfigure(2, weight=0)  # button row

    def open_readme(self):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = ReadmeWindow(
            self.main_frame,
            on_close_callback=lambda: self.on_selection_change(self.previous_selection)
        )

    def on_selection_change(self, selection):
        self.previous_selection = selection
        if self.current_window:
            self.current_window.destroy()
        if selection == "EIS":
            self.current_window = EISWindow(self.plot_frame, self.controls_frame, self.button_frame, self.toolbar_frame, self.temperature_widget)

    def on_close(self):
        os._exit(0)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
