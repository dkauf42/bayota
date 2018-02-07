#!/usr/bin/env python

"""
Frame for control buttons (like play/pause, mute, turn images on/off)
"""
import os

import tkinter as tk
import tkinter.ttk as ttk
    
# File Paths are specified.
#mainscript_dir = os.path.dirname(__main__.__file__)  # <-- absolute dir of the main script
script_dir = os.path.dirname(__file__)  # <-- absolute dir of this script


class TextBox(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.infostr = "extra info"
        
        # We need to get ttk.Label colors to work properly on OS X
        style = ttk.Style()
        style.theme_use('classic')

        self.infobox = None
        self.create_textdisplay()

    def create_textdisplay(self):
        # Label that displays miscellaneous info
        self.infobox = tk.Label(self, text=self.infostr,
                                bg="white", fg="dark blue",
                                font=('Helvetica Bold', 22),
                                justify='center',
                                wraplength=300)
        self.infobox.grid(row=0, column=0)
        #self.left_frame.grid_columnconfigure(0, weight=1)
    
    def displayinfo(self, info):
        self.infobox.configure(text=info)
    
    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False
