import tkinter as tk
import tkinter.ttk as ttk
from collections import namedtuple
import pandas as pd

from sandbox.gui.useframes.DualBox import DualBox


class MetadataFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to hold instance metadata options for the optimization configuration window"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.entry_optname = None
        self.entry_optdesc = None

        self.dropdown_baseyr = None
        self.dropdown_basecond = None
        self.dropdown_wastewtr = None
        self.dropdown_costprofile = None
        self.dropdown_geoscale = None
        self.geoareabox = None

        self.save_button = None

        self.results = None
        self.closedbyuser = False

        self.create_subframes()

        self.qrysource = None

    def create_subframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        self.rowconfigure(0, minsize=40)

        self.grid_columnconfigure(1, weight=1)

        # Text Labels
        tk.Label(self, text="Optimization Name", anchor='e').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Description", anchor="e").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Base Year", anchor='e').grid(row=3, column=0, sticky=tk.E)
        tk.Label(self, text="Base Condition", anchor="e").grid(row=4, column=0, sticky=tk.E)
        tk.Label(self, text="Wastewater Data", anchor="e").grid(row=5, column=0, sticky=tk.E)
        tk.Label(self, text="Cost Profile", anchor="e").grid(row=6, column=0, sticky=tk.E)
        tk.Label(self, text="Geographic Scale", anchor="e").grid(row=7, column=0, sticky=tk.E)

        # Text Entry Boxes
        self.entry_optname = self.my_textentry(defaultvalue='TestOne')
        self.entry_optname.grid(row=1, column=1, sticky=tk.W)
        self.entry_optdesc = self.my_textentry(defaultvalue='TestOneDescription')
        self.entry_optdesc.grid(row=2, column=1, sticky=tk.W)

        # Drop Down Menus (Base Year)
        options_list = ["N/A"]
        self.dropdown_baseyr = self.my_dropdown(options_list)
        self.dropdown_baseyr.grid(row=3, column=1, sticky='we')
        self.dropdown_baseyr.current(0)
        # (Base Condition)
        options_list = ["N/A"]
        self.dropdown_basecond = self.my_dropdown(options_list)
        self.dropdown_basecond.grid(row=4, column=1, sticky='we')
        self.dropdown_basecond.current(0)
        # (Wastewater Data)
        options_list = ["N/A"]
        self.dropdown_wastewtr = self.my_dropdown(options_list)
        self.dropdown_wastewtr.grid(row=5, column=1, sticky='we')
        self.dropdown_wastewtr.current(0)
        # (Cost Profile)
        options_list = ["N/A"]
        self.dropdown_costprofile = self.my_dropdown(options_list)
        self.dropdown_costprofile.grid(row=6, column=1, sticky='we')
        self.dropdown_costprofile.current(0)
        # (Geographic Scale)
        options_list = ["N/A"]
        self.dropdown_geoscale = self.my_dropdown(options_list)
        self.dropdown_geoscale.grid(row=7, column=1, sticky='we')
        self.dropdown_geoscale.current(0)
        self.dropdown_geoscale.bind("<<ComboboxSelected>>", self.update_geoareabox_options)

        # Dual Listbox
        options_list = ['N/A']
        self.geoareabox = DualBox(self, options_list)
        self.geoareabox.grid(row=8, column=1, sticky='we')

        # Save Button
        self.save_button = ttk.Button(self, text='Submit')
        self.save_button.grid(row=9, column=1, sticky='we')

    def load_options(self, queries=None):
        self.qrysource = queries

        self.dropdown_baseyr['values'] = ['Select Base Year'] + queries.base_year_names()
        self.dropdown_baseyr.current(0)
        self.dropdown_basecond['values'] = ['Select Base Condition'] + queries.base_condition_names()
        self.dropdown_basecond.current(0)
        self.dropdown_wastewtr['values'] = ['Select Wastewater Data Set'] + queries.wastewaterdata_names()
        self.dropdown_wastewtr.current(0)
        self.dropdown_costprofile['values'] = ['Select Cost Profile'] + queries.costprofile_names()
        self.dropdown_costprofile.current(0)
        self.dropdown_geoscale['values'] = ['Select Geographic Scale'] + \
            queries.all_geotypes().geographytypefullname.tolist()
        self.dropdown_geoscale.current(0)

        self.update_geoareabox_options()

    def update_geoareabox_options(self, event=None):
        geoscale = self.dropdown_geoscale.get()

        areas = self.qrysource.geonames_from_geotypename(geotype=geoscale)
        if isinstance(areas, pd.Series):
            areas = areas.tolist()

        self.geoareabox.set_new_left_side_items(areas)

    def get_results(self):
        Optmeta = namedtuple('metadata', 'name description baseyear basecond '
                                         'wastewater costprofile '
                                         'scale area')
        self.results = Optmeta(name=self.entry_optname.get(),
                               description=self.entry_optdesc.get(),
                               baseyear=self.dropdown_baseyr.get(),
                               basecond=self.dropdown_basecond.get(),
                               wastewater=self.dropdown_wastewtr.get(),
                               costprofile=self.dropdown_costprofile.get(),
                               scale=self.dropdown_geoscale.get(),
                               area=self.geoareabox.get_selection())
        return self.results

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist, state="readonly")

    def my_textentry(self, defaultvalue):
        entry_box = tk.Entry(self, foreground='light gray')
        entry_box.insert(0, defaultvalue)

        entry_box.bind("<FocusIn>", lambda args: entry_box.delete('0', 'end'))
        entry_box.bind("<FocusIn>", lambda args: entry_box.configure(foreground='black'))

        return entry_box
