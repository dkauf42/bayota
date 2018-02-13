import sys
from collections import namedtuple
import tkinter as tk
import tkinter.ttk as ttk

from gui.toplevelframes.topframe import TopFrame
from gui.toplevelframes.metadata_frame import MetadataFrame
from gui.toplevelframes.freeparam_frame import FreeParamFrame
from gui.toplevelframes.additionalconstraints_frame import AdditionalConstraintsFrame
from gui.useframes.toggleframe import ToggledFrame


class MainWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The optimization configuration window"""
        my_bgcolor = "bisque"
        tk.Frame.__init__(self, parent, *args, **kwargs, background=my_bgcolor)
        self.parent = parent
        
        # We need to get ttk.Label colors to work properly on OS X
        style = ttk.Style()
        style.theme_use('classic')
        
        style.configure('big.TLabel', relief='flat',
                        background='dark gray', font=('Helvetica', 16))
        style.configure("red.Horizontal.TProgressbar", foreground='blue', background='blue')

        self.closedbyuser = False
        self.results = None

        # In-window Title
        self.top_frame = TopFrame(self, background=my_bgcolor)
        self.top_frame.pack(side='top', fill='x', expand=True)

        # Collapsible/Toggled Frames
        collapsibleFrame = tk.Frame(self)
        collapsibleFrame.pack(fill=None, expand=False)
        # Toggle Frame #1
        t = ToggledFrame(collapsibleFrame, text='1. Instance Metadata', relief="raised", borderwidth=1)
        t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        t.config(width=800, height=100)
        t.update()

        self.metadataframe = MetadataFrame(t.sub_frame)
        self.metadataframe.pack(side="left")

        # Toggle Frame #2
        t2 = ToggledFrame(collapsibleFrame, text='2. Free Parameter Groups', relief="raised", borderwidth=1)
        t2.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.freeparamframe = FreeParamFrame(t2.sub_frame)
        self.freeparamframe.pack(side="left")

        # Toggle Frame #3
        t3 = ToggledFrame(collapsibleFrame, text='3. Additional Constraints/Bounds', relief="raised", borderwidth=1)
        t3.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")

        self.additionalconstraintsframe = AdditionalConstraintsFrame(t3.sub_frame)
        self.additionalconstraintsframe.pack(side="left")
        
        # Set up keyboard control of the window
        self.parent.bind('<Escape>', self.on_mainwindow_closing)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_mainwindow_closing)

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    # def close_and_submit(self):
    #     Optmeta = namedtuple('metadata', 'name description baseyear basecond '
    #                                      'wastewater costprofile annualbmps '
    #                                      'agency sector scale area')
    #     self.results = Optmeta(name=self.left_frame.entry_optname.get(),
    #                            description=self.left_frame.entry_optdesc.get(),
    #                            baseyear=self.right_frame.optionsbox_baseyr.get(),
    #                            basecond=self.right_frame.optionsbox_basecond.get(),
    #                            wastewater=self.right_frame.optionsbox_wastewtr.get(),
    #                            costprofile=self.right_frame.optionsbox_costprofile.get(),
    #                            annualbmps=self.right_frame.button_annualbmps.val.get(),
    #                            agency=self.left_frame.optionsbox_agency.get(),
    #                            sector=self.left_frame.optionsbox_sector.get(),
    #                            scale=self.left_frame.optionsbox_geoscale.get(),
    #                            area=self.left_frame.geodualbox.get_selection())
    #
    #     self.closedbyuser = True
    #     #print('MainWindow.close_and_submit: closing and submitting...')
    #
    #     self.parent.results = self.results
    #     self.quit()
        
    def on_mainwindow_closing(self, event=None):
        self.closedbyuser = True
        #print('MainWindow.on_mainwindow_closing: closing...')

        self.destroy()
        self.parent.destroy()

        exception_type, exception_value, exception_traceback = sys.exc_info()
        self.__exit__(exception_type, exception_value, exception_traceback)
