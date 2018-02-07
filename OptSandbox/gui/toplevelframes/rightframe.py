import os

import tkinter as tk
    
# File Paths are specified.
script_dir = os.path.dirname(__file__)  # <-- absolute dir of this script


class RightFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The right-hand side frame of the optimization configuration window"""
    
        # Use the __init__ of the superclass to create the actual frame
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        self.create_rightframes()
        
    def create_rightframes(self):
        
        self.columnconfigure(0, minsize=150)
        self.columnconfigure(1, minsize=300)
        
        self.grid_columnconfigure(1, weight=1)
