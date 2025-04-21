import customtkinter as ctk
from gui.markdown import RichText
import os

class ReadmeWindow(ctk.CTkFrame):
    """
    Class dedicated to displaying contents of README.md
    """

    def __init__(self, parent, on_close_callback):
        """
        Initialize the ReadmeWindow

        Args:
            parent: parent widget in which this frame will be placed
            on_close_callback (callable, optional): A callback function to call when the README window closes.
        """
        super().__init__(parent)
        self.on_close_callback = on_close_callback

        self.configure_frame()
        self.create_widgets()
        self.load_readme_content()

    def configure_frame(self):
        self.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        # Frame for README text with scroll
        self.readme_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.readme_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.readme_frame.grid_columnconfigure(0, weight=1)
        self.readme_frame.grid_rowconfigure(0, weight=1)

        # Create and configure the default font
        default_font = ctk.CTkFont(family="TkDefaultFont", size=12)

        # Create a scrollable frame container
        self.scrollable_frame = ctk.CTkScrollableFrame(self.readme_frame, fg_color="transparent")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Text area for the README content using RichText
        self.readme_text_area = RichText(
            self.scrollable_frame,
            wrap=ctk.WORD,
            font=default_font,
            height=300,  # Set a default height
        )
        self.readme_text_area.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Close button frame to ensure it stays at bottom
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.button_frame.grid_columnconfigure(0, weight=1)

        # Close button
        self.close_button = ctk.CTkButton(
            self.button_frame,
            text="Close README",
            command=self.close,
            font=default_font,
            width=120
        )
        self.close_button.grid(row=0, column=0, pady=5)

    def load_readme_content(self):
        try:
            readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
            with open(readme_path, "r") as file:
                content = file.read()
            # Parse and insert the markdown content
            self.parse_and_insert_markdown(content)
            self.readme_text_area.configure(state="disabled")  # Make text read-only.
        except FileNotFoundError:
            self.readme_text_area.insert("end", "README.md file not found")

    def parse_and_insert_markdown(self, content):
        """Parse markdown content and insert it into the text area."""
        lines = content.split("\n")
        current_indent = 0

        for line in lines:
            # Handle empty lines
            if line.strip() == "":
                self.readme_text_area.insert("end", "\n")
                continue

            # Count leading spaces to determine indentation level
            indent = len(line) - len(line.lstrip())
            indent_level = indent // 2  # 2 spaces per indentation level

            # Remove leading spaces for processing
            line = line.strip()

            # Handle headers
            if line.startswith("# "):
                self.readme_text_area.insert("end", line[2:], "h1")
                self.readme_text_area.insert("end", "\n\n")
            elif line.startswith("## "):
                self.readme_text_area.insert("end", line[3:], "h2")
                self.readme_text_area.insert("end", "\n\n")
            elif line.startswith("### "):
                self.readme_text_area.insert("end", line[4:], "h3")
                self.readme_text_area.insert("end", "\n\n")
            # Handle bullet points
            elif line.startswith("- "):
                self.readme_text_area.insert_bullet("end", line[2:], indent_level)
                self.readme_text_area.insert("end", "\n")
            # Handle regular text
            else:
                self.readme_text_area.insert("end", line + "\n")

    def close(self):
        """Handle closing the README window."""
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()
