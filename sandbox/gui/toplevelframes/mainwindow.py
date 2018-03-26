import tkinter as tk
import tkinter.ttk as ttk

from sandbox.gui.toplevelframes.topframe import TopFrame
from sandbox.gui.toplevelframes.metadata_frame import MetadataFrame
from sandbox.gui.toplevelframes.freeparam_frame import FreeParamFrame
from sandbox.gui.toplevelframes.additionalconstraints_frame import AdditionalConstraintsFrame
from sandbox.gui.useframes.toggleframe import ToggledFrame


class MainWindow(tk.Frame):
    def __init__(self, parent, optinstance, no_gui=False, *args, **kwargs):
        """The optimization configuration window"""
        my_bgcolor = "bisque"
        tk.Frame.__init__(self, parent, *args, **kwargs, background=my_bgcolor)
        self.parent = parent

        self.optinstance = optinstance
        self.queries = optinstance.queries
        self.no_gui = no_gui
        
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
        self.t = ToggledFrame(collapsible_frame, text='1. Instance Metadata',
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

        self.load_metadata_options()

        if no_gui:
            self.skipgui_and_use_default_test()

    def __enter__(self):
        return self
        
    def __exit__(self, exception_type, exception_value, exception_traceback):
        return False

    def skipgui_and_use_default_test(self):
        """For Testing Purposes"""
        self.optinstance.name = 'TestOne'
        self.optinstance.description = 'TestOneDescription'
        self.optinstance.baseyear = '1995'
        self.optinstance.basecondname = 'Example_BaseCond2'
        self.optinstance.wastewatername = 'Example_WW1'
        self.optinstance.costprofilename = 'Example_CostProfile1'
        self.optinstance.geoscalename = 'County'
        self.optinstance.geoareanames = ['Adams, PA']

        self.optinstance.geographies_included = self.queries.source.\
            get_lrseg_table(scale=self.optinstance.geoscalename, areanames=self.optinstance.geoareanames)
        self.optinstance.agencies_included = self.queries.base.\
            get_agencies_in_lrsegs(lrsegs=self.optinstance.geographies_included.LandRiverSegment)
        self.optinstance.sectors_included = self.queries.source.get_all_sector_names()

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.optinstance.generate_emptyparametermatrices()
        self.optinstance.mark_eligibility()
        self.optinstance.generate_boundsmatrices()

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

    def load_metadata_options(self):
        self.metadataframe.load_options(self.queries.source)

    def save_metadata(self):
        print('mainwindow:save_metadata: saving metadata...')
        self.optinstance.save_metadata(self.metadataframe.get_results())
        lrseg_table = self.queries.source.get_lrseg_table(scale=self.optinstance.geoscalename,
                                                          areanames=self.optinstance.geoareanames)
        self.optinstance.set_geography(geotable=lrseg_table)

    def load_freeparamgroup_options(self):
        self.freeparamframe.update_box_options(queries=self.queries, optinstance=self.optinstance)

    def save_freeparamgroups(self):
        print('mainwindow:save_freeparamgroups: saving free parameter groups...')
        self.optinstance.save_freeparamgrps(self.freeparamframe.get_results())

    def load_constraint_options(self):  # TODO:add constraint widgets
        self.additionalconstraintsframe.update_box_options(optinstance=self.optinstance)

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
