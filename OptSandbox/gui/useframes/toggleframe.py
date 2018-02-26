import tkinter as tk
import tkinter.ttk as ttk


class ToggledFrame(tk.Frame):

    def __init__(self, parent, text="", secondcommand=None, *args, **options):
        tk.Frame.__init__(self, parent, *args, **options)
        self.parent = parent

        self.show = tk.IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        self.frame_label = ttk.Label(self.title_frame, text=text)
        self.frame_label.pack(side="left", fill="x", expand=1)

        self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+',
                                             command=self.sequence(self.toggle, secondcommand),
                                             variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side="left")

        self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

        self.style = ttk.Style()
        self.saved = False

    def toggle(self, source=None):
        if bool(self.show.get()):
            # if the frame was closed, then open it
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(width=4)
            self.toggle_button.configure(text='save')
        else:
            # if the frame was opened, then close it
            self.sub_frame.forget()
            self.toggle_button.configure(width=2)
            self.toggle_button.configure(text='+')

            self.saved = True

    def greyout(self):
        self.style.configure("Grey.TLabel", foreground="grey")
        self.frame_label.config(style="Grey.TLabel")
        self.toggle_button.config(state=tk.DISABLED)

    def ungrey(self):
        self.style.configure("Black.TLabel", foreground="black")
        self.frame_label.config(style="Black.TLabel")
        self.toggle_button.config(state='normal')

    def sequence(self, *functions):
        """A method that allows multiple callback functions to be specified for a single tkinter widget"""
        def func(*args, **kwargs):
            return_value = None
            for funcshin in functions:
                if funcshin is not None:
                    return_value = funcshin(source=self, *args, **kwargs)
            return return_value
        return func
