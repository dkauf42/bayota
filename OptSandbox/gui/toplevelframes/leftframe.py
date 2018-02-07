import tkinter as tk
import tkinter.ttk as ttk

from gui.useframes.dualbox import DualBox


class LeftFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The left-hand side frame of the optimization configuration window"""
    
        # Use the __init__ of the superclass to create the actual frame
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.entry_optname = None
        self.entry_optdesc = None

        self.optionsbox_agency = None
        self.optionsbox_sector = None
        self.optionsbox_geoscale = None
        self.geodualbox = None

        self.create_leftframes()

        self.results = None
    
    def create_leftframes(self):

        self.columnconfigure(0, minsize=100)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=100)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Text Labels
        tk.Label(self, text="Optimization Name", anchor='e').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Description", anchor="e").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Agencies", anchor="e").grid(row=3, column=0, sticky=tk.E)
        tk.Label(self, text="Sectors", anchor="e").grid(row=4, column=0, sticky=tk.E)
        tk.Label(self, text="Geographic Scale", anchor="e").grid(row=5, column=0, sticky=tk.E)

        # Text Entry Boxes
        self.entry_optname = self.my_textentry(defaultvalue='TestOne')
        self.entry_optname.grid(row=1, column=1, sticky=tk.W)
        self.entry_optdesc = self.my_textentry(defaultvalue='TestOneDescription')
        self.entry_optdesc.grid(row=2, column=1, sticky=tk.W)

        # Drop Down Menu (Agency)
        options_list = ["All Agencies", "Agency B", "Agency C", "Agency D", "Agency E", "Agency F", "Agency G", "Agency H"]
        self.optionsbox_agency = self.my_dropdown(options_list)
        self.optionsbox_agency.grid(row=3, column=1, sticky='we')
        self.optionsbox_agency.current(0)

        # Drop Down Menu (Sector)
        options_list = ["All Sectors", "Sector 0002", "Sector 0003", "Sector 0004", "Sector 0005", "Sector 0006"]
        self.optionsbox_sector = self.my_dropdown(options_list)
        self.optionsbox_sector.grid(row=4, column=1, sticky='we')
        self.optionsbox_sector.current(0)

        # Drop Down Menu (Geographic Scale)
        options_list = ["County", "Large Scale", "Medium Scale", "Small Scale"]
        self.optionsbox_geoscale = self.my_dropdown(options_list)
        self.optionsbox_geoscale.grid(row=5, column=1, sticky='we')
        self.optionsbox_geoscale.current(0)

        # Dual Listbox
        options_list = ['Anne Arundel', 'Talbot', 'Caroline', 'Lancaster']
        self.geodualbox = DualBox(self, options_list)
        self.geodualbox.grid(row=6, column=1, sticky='we')

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)

    def my_textentry(self, defaultvalue):
        entry_box = tk.Entry(self, foreground='light gray')
        entry_box.insert(0, defaultvalue)

        entry_box.bind("<FocusIn>", lambda args: entry_box.delete('0', 'end'))
        entry_box.bind("<FocusIn>", lambda args: entry_box.configure(foreground='black'))

        return entry_box
