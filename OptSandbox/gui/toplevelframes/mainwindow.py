import sys
from collections import namedtuple
import tkinter as tk
import tkinter.ttk as ttk

from gui.toplevelframes.topframe import TopFrame
from gui.toplevelframes.bottomframe import BottomFrame
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
        self.results = None
        
        # GUI frames
        self.top_frame = TopFrame(self)
        self.bottom_frame = BottomFrame(self)
        self.left_frame = LeftFrame(self)
        self.right_frame = RightFrame(self)

        self.top_frame.pack(side='top', fill='x', expand=True)
        self.bottom_frame.pack(side='bottom', fill='x', expand=True)
        self.left_frame.pack(side='left', fill='both', expand=True)
        self.right_frame.pack(side='left', fill='both', expand=True)
        
        # Set up keyboard control of the window
        self.parent.bind('<Escape>', self.on_mainwindow_closing)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_mainwindow_closing)

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    def close_and_submit(self):
        Optmeta = namedtuple('metadata', 'name description baseyear basecond '
                                         'wastewater costprofile agency sector scale area')
        self.results = Optmeta(name=self.left_frame.entry_optname.get(),
                               description=self.left_frame.entry_optdesc.get(),
                               baseyear=self.right_frame.optionsbox_baseyr.get(),
                               basecond=self.right_frame.optionsbox_basecond.get(),
                               wastewater=self.right_frame.optionsbox_wastewtr.get(),
                               costprofile=self.right_frame.optionsbox_costprofile.get(),
                               agency=self.left_frame.optionsbox_agency.get(),
                               sector=self.left_frame.optionsbox_sector.get(),
                               scale=self.left_frame.optionsbox_geoscale.get(),
                               area=self.left_frame.geodualbox.get_selection())

        self.closedbyuser = True
        #print('MainWindow.close_and_submit: closing and submitting...')

        self.parent.results = self.results
        self.quit()
        
    def on_mainwindow_closing(self, event=None):
        self.closedbyuser = True
        #print('MainWindow.on_mainwindow_closing: closing...')

        self.destroy()
        self.parent.destroy()

        exception_type, exception_value, exception_traceback = sys.exc_info()
        self.__exit__(exception_type, exception_value, exception_traceback)
