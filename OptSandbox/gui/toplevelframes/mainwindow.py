import sys

import tkinter as tk
import tkinter.ttk as ttk

from gui.toplevelframes.leftframe import LeftFrame
from gui.toplevelframes.rightframe import RightFrame


class MainWindow(tk.Frame):
    def __init__(self, parent):
        """The optimization configuration window"""

        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        # We need to get ttk.Label colors to work properly on OS X
        style = ttk.Style()
        style.theme_use('classic')
        
        style.configure('big.TLabel', relief='flat',
                        background='dark gray', font=('Helvetica', 16))
        style.configure("red.Horizontal.TProgressbar", foreground='blue', background='blue')

        self.closedbyuser = False
        
        # GUI frames
        self.left_frame = LeftFrame(self)
        self.right_frame = RightFrame(self)  #, width=200, height=120)

        self.left_frame.pack(side='left', fill='both', expand=True)
        self.right_frame.pack(side='left', expand=True)
        
        # Set up keyboard control of the window
        self.parent.bind('<Escape>', self.on_mainwindow_closing)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_mainwindow_closing)

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    def close_and_submit(self):
        self.closedbyuser = True
        #print('MainWindow.close_and_submit: closing and submitting...')

        self.parent.results = self.left_frame.results
        self.quit()
        
    def on_mainwindow_closing(self, event=None):
        self.closedbyuser = True
        #print('MainWindow.on_mainwindow_closing: closing...')

        self.destroy()
        self.parent.destroy()

        exception_type, exception_value, exception_traceback = sys.exc_info()
        self.__exit__(exception_type, exception_value, exception_traceback)
