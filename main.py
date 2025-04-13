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
        self.geometry("800x480")
        self._set_appearance_mode("dark")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Custom variables
        self.current_window = None
        self.previous_selection = "EIS"

        # Custom functions
        self.setup_main_frame()
        self.setup_toolbar()
        self.setup_frames()
        self.on_selection_change("EIS")

    def setup_main_frame(self):
        """Main frame is an empty widget to place all other widgets within"""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)
        self.readme_text_area = None

    def setup_toolbar(self):
        """Frame for top row with readme and close buttons"""
        self.toolbar_frame = ctk.CTkFrame(self.main_frame)
        self.toolbar_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        readme_button = ctk.CTkButton(self.toolbar_frame, text="Open README", command=self.open_readme)
        readme_button.pack(side=ctk.LEFT, padx=10)

        close_button = ctk.CTkButton(self.toolbar_frame, text="Close", command=self.on_close)
        close_button.pack(side=ctk.RIGHT, padx=10)

    def setup_frames(self):
        # frame for plot
        self.plot_frame = ctk.CTkFrame(self.main_frame)
        self.plot_frame.grid(row=1, column=0, sticky="nsew")

        # frame for: experiment settings, analysis settings, experimental control, & results
        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=1, column=1, sticky="nsew")

        # frame for plot types
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def on_selection_change(self, selection):
        self.previous_selection = selection
        if self.current_window:
            self.current_window.destroy()
        if selection == "EIS":
            self.current_window = EISWindow(self.plot_frame, self.controls_frame, self.button_frame, self.toolbar_frame)

    def open_readme(self):
        if self.current_window:
            self.current_window.destroy()
        self.current_window = ReadmeWindow(
            self.main_frame,
            on_close_callback=lambda: self.on_selection_change(self.previous_selection)
        )

    def on_close(self):
        os._exit(0)

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
