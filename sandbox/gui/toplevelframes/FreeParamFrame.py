import tkinter as tk
import tkinter.ttk as ttk
from collections import namedtuple

from sandbox.gui.useframes.DualBox import DualBox


class FreeParamFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to specify which free parameter groups to open up for optimization algorithm tweaking"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.agencydualbox = None
        self.sectordualbox = None

        self.save_button = None

        self.results = None

        self.create_subframes()

    def create_subframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        self.rowconfigure(0, minsize=40)

        self.grid_columnconfigure(1, weight=1)

        # Text Labels
        tk.Label(self, text="Select From...", anchor='e').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Agencies", anchor="e").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Sectors", anchor='e').grid(row=3, column=0, sticky=tk.E)

        # Dual Listbox (Agencies)
        options_list = ['All Agencies', 'NONFED', 'FWS', '...']
        self.agencydualbox = DualBox(self, options_list)
        self.agencydualbox.grid(row=2, column=1, sticky='we')
        # (Sectors)
        options_list = ['All Sectors', 'Developed', 'Natural', '...']
        self.sectordualbox = DualBox(self, options_list)
        self.sectordualbox.grid(row=3, column=1, sticky='we')

        # Save Button
        self.save_button = ttk.Button(self, text='Submit')
        self.save_button.grid(row=9, column=1, sticky='we')

    def update_box_options(self, queries=None, optcase=None):
        """Populate first dualbox with agencies included in OptCase and second dualbox with all sectors

        Args:
            queries (TblJeeves):
            optcase (OptCase):
        """

        mylist = queries.agencycodes_from_lrsegids(lrsegids=optcase.lrsegids).agencycode.unique().tolist()
        self.agencydualbox.set_new_left_side_items(mylist)

        mylist = queries.all_names().tolist()
        self.sectordualbox.set_new_left_side_items(mylist)

    def get_results(self):
        Optmeta = namedtuple('freeparamgrps', 'agencies sectors')
        self.results = Optmeta(agencies=self.agencydualbox.get_selection(),
                               sectors=self.sectordualbox.get_selection())
        print('freeparamgrps results:')
        print(self.results)
        return self.results

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)

    def my_textentry(self, defaultvalue):
        entry_box = tk.Entry(self, foreground='light gray')
        entry_box.insert(0, defaultvalue)

        entry_box.bind("<FocusIn>", lambda args: entry_box.delete('0', 'end'))
        entry_box.bind("<FocusIn>", lambda args: entry_box.configure(foreground='black'))

        return entry_box
