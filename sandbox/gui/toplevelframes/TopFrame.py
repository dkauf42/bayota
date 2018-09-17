import tkinter as tk
import tkinter.ttk as ttk


class TopFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The top side frame of the optimization configuration window"""
    
        # Use the __init__ of the superclass to create the actual frame
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.textbox = None

        self.create_topframes()
    
    def create_topframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=50)
        self.grid_columnconfigure(1, weight=1)

        # We need to get ttk.Label colors to work properly on OS X
        style = ttk.Style()
        style.theme_use('classic')

        # Text Label
        self.textbox = tk.Label(self,
                                text='Optimization Instance Options',
                                bg="cornflower blue",
                                fg="dark blue",
                                font=('Helvetica Bold', 22),
                                justify='center',
                                wraplength=300)
        self.textbox.grid(row=0, column=1, sticky='we')
