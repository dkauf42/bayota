import tkinter as tk


class BottomFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The bottom side frame of the optimization configuration window"""

        # Use the __init__ of the superclass to create the actual frame
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.results = None

        self.create_bottomframes()

    def create_bottomframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=50)
        self.grid_columnconfigure(1, weight=1)

        # Submission Button
        tk.Button(self, text="Submit", command=self.my_submit).grid(row=0, column=1, sticky='we')

    def my_submit(self):
        self.parent.close_and_submit()
