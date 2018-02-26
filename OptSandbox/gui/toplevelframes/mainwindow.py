import sys
import tkinter as tk
import tkinter.ttk as ttk
from collections import namedtuple

from gui.toplevelframes.topframe import TopFrame
from gui.toplevelframes.metadata_frame import MetadataFrame
from gui.toplevelframes.freeparam_frame import FreeParamFrame
from gui.toplevelframes.additionalconstraints_frame import AdditionalConstraintsFrame
from gui.useframes.toggleframe import ToggledFrame


class MainWindow(tk.Frame):
    def __init__(self, parent, qrysource, optinstance, *args, **kwargs):
        """The optimization configuration window"""
        my_bgcolor = "bisque"
        tk.Frame.__init__(self, parent, *args, **kwargs, background=my_bgcolor)
        self.parent = parent
        self.qrysource = qrysource
        self.optinstance = optinstance
        
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
        # Toggle Frame #1 (METADATA)
        self.t = ToggledFrame(collapsibleFrame, text='1. Instance Metadata',
                              relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.t.config(width=800, height=100)
        #self.t.update()
        self.metadataframe = MetadataFrame(self.t.sub_frame)
        self.metadataframe.pack(side="left")
        # Toggle Frame #2 (FREE PARAMETER GROUPS)
        self.t2 = ToggledFrame(collapsibleFrame, text='2. Free Parameter Groups',
                               relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t2.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.freeparamframe = FreeParamFrame(self.t2.sub_frame)
        self.freeparamframe.pack(side="left")
        self.t2.greyout()
        # Toggle Frame #3 (ADDITIONAL CONSTRAINTS)
        self.t3 = ToggledFrame(collapsibleFrame, text='3. Additional Constraints/Bounds',
                               relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t3.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.additionalconstraintsframe = AdditionalConstraintsFrame(self.t3.sub_frame)
        self.additionalconstraintsframe.pack(side="left")
        self.t3.greyout()

        # Done Button
        self.done_button = tk.Button(self, text='Submit', command=self.close_and_submit)
        self.done_button.pack(side='top', fill='x', expand=True)
        
        # Set up keyboard control of the window
        self.parent.bind('<Escape>', self.on_mainwindow_closing)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_mainwindow_closing)

        self.load_metadata(qrysource=self.qrysource)

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    def toggleframe_closed(self, source=None):
        if source is self.t:
            if self.t.saved is True:
                if bool(self.t.show.get()):
                    # if the frame was closed before the toggle, then do nothing
                    pass
                else:
                    # if the frame was opened before the toggle, then save the form data
                    self.save_metadata()
                    self.t2.ungrey()
                    self.load_freeparamgroups(qrysource=self.qrysource, optinstance=self.optinstance)

        if source is self.t2:
            if self.t2.saved is True:
                self.t3.ungrey()

    def load_metadata(self, qrysource=None):
        self.metadataframe.load_options(qrysource)

    def save_metadata(self):
        self.optinstance.save_metadata(self.metadataframe.get_results())
        lrseg_table = self.qrysource.get_lrseg_table(scale=self.optinstance.geoscalename, areanames=self.optinstance.geoareanames)
        self.optinstance.set_geography(geotable=lrseg_table)

    def load_freeparamgroups(self, qrysource=None, optinstance=None):
        self.freeparamframe.update_box_options(qrysource, optinstance)

    def close_and_submit(self):
        pass
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
    #                            area=self.left_frame.geoareabox.get_selection())
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
