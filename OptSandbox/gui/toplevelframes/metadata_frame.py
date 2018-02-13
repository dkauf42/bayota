import tkinter as tk
import tkinter.ttk as ttk
from gui.useframes.dualbox import DualBox


class MetadataFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to hold instance metadata options for the optimization configuration window"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.entry_optname = None
        self.entry_optdesc = None

        self.optionsbox_baseyr = None
        self.optionsbox_basecond = None
        self.optionsbox_wastewtr = None
        self.optionsbox_costprofile = None
        self.optionsbox_geoscale = None
        self.geodualbox = None

        self.create_subframes()

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

        # Drop Down Menu (Base Year)
        options_list = ["N/A", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002"]
        self.optionsbox_baseyr = self.my_dropdown(options_list)
        self.optionsbox_baseyr.grid(row=3, column=1, sticky='we')
        self.optionsbox_baseyr.current(0)

        # Drop Down Menu (Base Condition)
        options_list = ["Base Progress 0000", "Base Progress 0001", "Base Progress 0002", "Base Progress 0003"]
        self.optionsbox_basecond = self.my_dropdown(options_list)
        self.optionsbox_basecond.grid(row=4, column=1, sticky='we')
        self.optionsbox_basecond.current(0)

        # Drop Down Menu (Wastewater Data)
        options_list = ["N/A", "Wastewater A", "Wastewater B", "Wastewater C", "Wastewater D"]
        self.optionsbox_wastewtr = self.my_dropdown(options_list)
        self.optionsbox_wastewtr.grid(row=5, column=1, sticky='we')
        self.optionsbox_wastewtr.current(0)

        # Drop Down Menu (Cost Profile)
        options_list = ["N/A", "Profile AAAA", "Profile BBBB", "Profile CCCC", "Profile DDDD", "Profile EEEE"]
        self.optionsbox_costprofile = self.my_dropdown(options_list)
        self.optionsbox_costprofile.grid(row=6, column=1, sticky='we')
        self.optionsbox_costprofile.current(0)

        # Drop Down Menu (Geographic Scale)
        options_list = ["County", "Large Scale", "Medium Scale", "Small Scale"]
        self.optionsbox_geoscale = self.my_dropdown(options_list)
        self.optionsbox_geoscale.grid(row=7, column=1, sticky='we')
        self.optionsbox_geoscale.current(0)

        # Dual Listbox
        options_list = ['Anne Arundel', 'Talbot', 'Caroline', 'Lancaster']
        self.geodualbox = DualBox(self, options_list)
        self.geodualbox.grid(row=8, column=1, sticky='we')

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)

    def my_textentry(self, defaultvalue):
        entry_box = tk.Entry(self, foreground='light gray')
        entry_box.insert(0, defaultvalue)

        entry_box.bind("<FocusIn>", lambda args: entry_box.delete('0', 'end'))
        entry_box.bind("<FocusIn>", lambda args: entry_box.configure(foreground='black'))

        return entry_box
