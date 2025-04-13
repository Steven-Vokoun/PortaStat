import tkinter as tk
from tkinter import font as tkFont

class RichText(tk.Text):
    """
    Class mainly from StackOverflow

    https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter/63105641#63105641
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_font = tkFont.nametofont(self.cget("font"))

        em = default_font.measure("m")
        default_size = default_font.cget("size")
        bold_font = tkFont.Font(**default_font.configure())
        italic_font = tkFont.Font(**default_font.configure())
        
        # Configure fonts for different header levels
        h1_font = tkFont.Font(**default_font.configure())
        h2_font = tkFont.Font(**default_font.configure())
        h3_font = tkFont.Font(**default_font.configure())

        bold_font.configure(weight="bold")
        italic_font.configure(slant="italic")
        h1_font.configure(size=int(default_size*2), weight="bold")
        h2_font.configure(size=int(default_size*1.5), weight="bold")
        h3_font.configure(size=int(default_size*1.2), weight="bold")

        self.tag_configure("bold", font=bold_font)
        self.tag_configure("italic", font=italic_font)
        self.tag_configure("h1", font=h1_font, spacing3=default_size)
        self.tag_configure("h2", font=h2_font, spacing3=default_size)
        self.tag_configure("h3", font=h3_font, spacing3=default_size)

        # Configure bullet point tags for different indentation levels
        self.bullet_tags = []
        for i in range(5):  # Support up to 5 levels of nesting
            lmargin1 = em * (i + 1)
            lmargin2 = lmargin1 + default_font.measure("\u2022 ")
            tag_name = f"bullet_{i}"
            self.tag_configure(tag_name, lmargin1=lmargin1, lmargin2=lmargin2)
            self.bullet_tags.append(tag_name)

    def insert_bullet(self, index, text, indent_level=0):
        """Insert a bullet point with the specified indentation level."""
        tag = self.bullet_tags[min(indent_level, len(self.bullet_tags) - 1)]
        self.insert(index, f"\u2022 {text}", tag)