import tkinter as tk
import tkinter.ttk as ttk


class RightFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The right-hand side frame of the optimization configuration window"""
    
        # Use the __init__ of the superclass to create the actual frame
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.optionsbox_baseyr = None
        self.optionsbox_basecond = None
        self.optionsbox_wastewtr = None
        
        self.create_rightframes()
        
    def create_rightframes(self):
        
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        
        self.grid_columnconfigure(1, weight=1)

        # Text Labels
        tk.Label(self, text="Base Year", anchor='e').grid(row=0, column=0, sticky=tk.E)
        tk.Label(self, text="Base Condition", anchor="e").grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Wastewater Data", anchor="e").grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Cost Profile", anchor="e").grid(row=3, column=0, sticky=tk.E)

        # Drop Down Menu (Base Year)
        options_list = ["1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002"]
        self.optionsbox_baseyr = self.my_dropdown(options_list)
        self.optionsbox_baseyr.grid(row=0, column=1, sticky='we')
        self.optionsbox_baseyr.current(0)

        # Drop Down Menu (Base Condition)
        options_list = ["Base Progress 0000", "Base Progress 0001", "Base Progress 0002", "Base Progress 0003"]
        self.optionsbox_basecond = self.my_dropdown(options_list)
        self.optionsbox_basecond.grid(row=1, column=1, sticky='we')
        self.optionsbox_basecond.current(0)

        # Drop Down Menu (Base Condition)
        options_list = ["Wastewater A", "Wastewater B", "Wastewater C", "Wastewater D"]
        self.optionsbox_wastewtr = self.my_dropdown(options_list)
        self.optionsbox_wastewtr.grid(row=2, column=1, sticky='we')
        self.optionsbox_wastewtr.current(0)

        # Drop Down Menu (Cost Profile)
        options_list = ["Profile AAAA", "Profile BBBB", "Profile CCCC", "Profile DDDD", "Profile EEEE"]
        self.optionsbox_wastewtr = self.my_dropdown(options_list)
        self.optionsbox_wastewtr.grid(row=3, column=1, sticky='we')
        self.optionsbox_wastewtr.current(0)

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)
