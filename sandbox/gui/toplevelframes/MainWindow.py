import tkinter as tk
import tkinter.ttk as ttk

from sandbox.gui.toplevelframes.TopFrame import TopFrame
from sandbox.gui.toplevelframes.MetadataFrame import MetadataFrame
from sandbox.gui.toplevelframes.FreeParamFrame import FreeParamFrame
from sandbox.gui.toplevelframes.AdditionalConstraintsFrame import AdditionalConstraintsFrame
from sandbox.gui.useframes.ToggleFrame import ToggledFrame


class MainWindow(tk.Frame):
    def __init__(self, parent, optcase=None, *args, **kwargs):
        """The optimization configuration window"""
        my_bgcolor = 'cornflower blue'
        tk.Frame.__init__(self, parent, optcase=None, *args, **kwargs, background=my_bgcolor)
        self.parent = parent

        self.optcase = optcase
        
        # We need to get ttk.Label colors to work properly on OS X
        self.style = ttk.Style()
        self.style.theme_use('classic')

        self.style.configure("Grey.TButton", foreground="grey")
        self.style.configure("Black.TButton", foreground="black")

        self.closedbyuser = False
        self.results = None

        # In-window Title
        self.top_frame = TopFrame(self, background=my_bgcolor)
        self.top_frame.pack(side='top', fill='x', expand=True)

        # Skip Button for doing default test
        self.skipbutton = tk.Button(self, text='defaulttest', command=self.skipgui_and_use_default_test)
        self.skipbutton.pack(side="top", fill=None, expand=False)

        # Collapsible/Toggled Frames
        collapsible_frame = tk.Frame(self)
        collapsible_frame.pack(fill=None, expand=False)
        # Toggle Frame #1 (METADATA)
        self.t = ToggledFrame(collapsible_frame, text='1. Instance MetaData',
                              relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.t.config(width=800, height=100)
        self.metadataframe = MetadataFrame(self.t.sub_frame)
        self.metadataframe.pack(side="left")
        self.metadataframe.save_button.config(command=lambda: self.toggleframe_togglefromanotherbutton(source=self.t))
        # Toggle Frame #2 (FREE PARAMETER GROUPS)
        self.t2 = ToggledFrame(collapsible_frame, text='2. Free Parameter Groups',
                               relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t2.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.freeparamframe = FreeParamFrame(self.t2.sub_frame)
        self.freeparamframe.pack(side="left")
        self.t2.greyout()
        self.freeparamframe.save_button.config(command=lambda: self.toggleframe_togglefromanotherbutton(source=self.t2))
        # Toggle Frame #3 (ADDITIONAL CONSTRAINTS)
        self.t3 = ToggledFrame(collapsible_frame, text='3. Additional Constraints/Bounds',
                               relief="raised", borderwidth=1, secondcommand=self.toggleframe_closed)
        self.t3.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.additionalconstraintsframe = AdditionalConstraintsFrame(self.t3.sub_frame)
        self.additionalconstraintsframe.pack(side="left")
        self.t3.greyout()

        # Done Button
        self.done_button = ttk.Button(self, text='Submit', command=self.close_and_submit)
        self.done_button.pack(side='top', fill='x', expand=False)
        self.done_button.config(style="Grey.TButton")
        self.done_button.config(state=tk.DISABLED)
        
        # Set up keyboard control of the window
        self.parent.bind('<Escape>', self.on_mainwindow_closing)
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_mainwindow_closing)

        self.metadataframe.load_options(self.optcase.jeeves)

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    def skipgui_and_use_default_test(self):
        """For Testing Purposes"""
        # self.optcase.loadexample(name='adamscounty')
        self.optcase.set_metadata_to_example(name='adams_and_annearundel')
        # self.optcase = OptCase.loadexample(name='adams_and_annearundel')

        self.close_and_submit()

    def toggleframe_togglefromanotherbutton(self, event=None, source=None):
        source.toggle_fromotherbutton(event=event, source=source)
        self.toggleframe_closed(source=source)

    def toggleframe_closed(self, event=None, source=None):
        if source is self.t:
            if source.saved is True:
                if bool(source.show.get()):
                    # if the frame was closed before the toggle, then do nothing
                    pass
                else:
                    # if the frame was opened before the toggle, then save the form data
                    self.save_metadata()
                    self.t2.ungrey()
                    self.load_freeparamgroup_options()
                    self.t2.toggle_fromotherbutton()

        if source is self.t2:
            if source.saved is True:
                if bool(source.show.get()):
                    # if the frame was closed before the toggle, then do nothing
                    pass
                else:
                    fpgresults = self.freeparamframe.get_results()
                    if (not fpgresults.agencies) & (not fpgresults.sectors):  # if they're both empty, then do nothing
                        pass
                    else:
                        # if the frame was opened before the toggle, then save the form data
                        self.save_freeparamgroups()
                        self.t3.ungrey()
                        self.load_constraint_options()
                        self.t3.toggle_fromotherbutton()

        if source is self.t3:
            if self.t2.saved is True & self.t.saved is True:
                self.done_button.config(style="Black.TButton")
                self.done_button.config(state='normal')

            if self.t3.saved is True:
                if bool(self.t3.show.get()):
                    # if the frame was closed before the toggle, then do nothing
                    pass
                else:
                    # if the frame was opened before the toggle, then save the form data
                    self.save_constraints()

    def save_metadata(self):
        print('mainwindow:set_metadata: saving metadata...')
        mr = self.metadataframe.get_results()
        self.optcase.set_metadata(name=mr.name, description=mr.description, baseyear=mr.baseyear,
                                  basecondname=mr.basecondname, wastewatername=mr.wastewatername,
                                  costprofilename=mr.costprofilename,
                                  geoscalename=mr.scale, geoareanames=mr.areanames)

    def load_freeparamgroup_options(self):
        self.freeparamframe.update_box_options(jeeves=self.optcase.jeeves, optcase=self.optcase)

    def save_freeparamgroups(self):
        print('mainwindow:save_freeparamgroups: saving free parameter groups...')
        self.optcase.set_decisionspace_agencies_and_sectors(agencycodes=self.freeparamframe.get_results().agencies,
                                                            sectornames=self.freeparamframe.get_results().sectors)

    def load_constraint_options(self):  # TODO:add constraint widgets
        self.additionalconstraintsframe.update_box_options(optcase=self.optcase)

    def save_constraints(self):  # TODO:add constraint widgets
        pass

    def close_and_submit(self):
        print('MainWindow.close_and_submit')
        self.parent.results = self.results
        self.closedbyuser = True
        self.quit()
        
    def on_mainwindow_closing(self, event=None):
        self.closedbyuser = True
        raise SystemExit('MainWindow.on_mainwindow_closing: window closed')
