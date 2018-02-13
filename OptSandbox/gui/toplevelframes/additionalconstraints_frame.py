import tkinter as tk
import tkinter.ttk as ttk


class AdditionalConstraintsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to specify additional constraints/bounds on free parameters"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.optionsbox_bmp1 = None
        self.optionsbox_bmp2 = None
        self.optionsbox_bmp3 = None

        self.create_subframes()

    def create_subframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        self.rowconfigure(0, minsize=40)

        self.grid_columnconfigure(1, weight=1)

        # Text Labels
        tk.Label(self, text="BMP #1", anchor='e').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="BMP #2", anchor="e").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="BMP #3", anchor='e').grid(row=3, column=0, sticky=tk.E)

        # Drop Down Menu (Base Year)
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp1 = self.my_dropdown(options_list)
        self.optionsbox_bmp1.grid(row=1, column=1, sticky='we')
        self.optionsbox_bmp1.current(0)

        # Drop Down Menu (Base Condition)
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp2 = self.my_dropdown(options_list)
        self.optionsbox_bmp2.grid(row=2, column=1, sticky='we')
        self.optionsbox_bmp2.current(0)

        # Drop Down Menu (Wastewater Data)
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp3 = self.my_dropdown(options_list)
        self.optionsbox_bmp3.grid(row=3, column=1, sticky='we')
        self.optionsbox_bmp3.current(0)

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)
