import tkinter as tk
import tkinter.ttk as ttk
from gui.useframes.MyRangeSliderFrame3 import MyRangeSliderFrame3


class AdditionalConstraintsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to specify additional constraints/bounds on free parameters"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.optionsbox_bmp1 = None
        self.optionsbox_bmp2 = None
        self.optionsbox_bmp3 = None
        self.noconstraints_button = None

        self.__snapToTicksCheckVar = tk.IntVar()
        self.__snapToTicksCheckVar.set(int(0))
        self.__snapToTicks = None
        self.sliderframe1 = None
        self.sliderframe2 = None

        self.checkvar = tk.IntVar(value=1)

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
        tk.Label(self, text="BMP #4", anchor='e').grid(row=4, column=0, sticky=tk.E)

        # No Constraints Button
        self.noconstraints_button = tk.Checkbutton(self, width=1, text='No Constraints',
                                                   state='normal', variable=self.checkvar)
        self.noconstraints_button.grid(row=0, column=1, sticky='we')

        # SnapToTicks Button
        self.__snapToTicks = tk.Checkbutton(self,
                                            text="Snap To Ticks",
                                            command=self.clickallsnaptoticks,
                                            variable=self.__snapToTicksCheckVar,
                                            onvalue="1",
                                            offvalue="0")
        self.__snapToTicks.grid(row=0, column=2, sticky='we')

        # Drop Down Menu
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp1 = self.my_dropdown(options_list)
        self.optionsbox_bmp1.grid(row=1, column=1, sticky='we')
        self.optionsbox_bmp1.current(0)

        # Drop Down Menu
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp2 = self.my_dropdown(options_list)
        self.optionsbox_bmp2.grid(row=2, column=1, sticky='we')
        self.optionsbox_bmp2.current(0)

        # Drop Down Menu
        options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        self.optionsbox_bmp3 = self.my_dropdown(options_list)
        self.optionsbox_bmp3.grid(row=3, column=1, sticky='we')
        self.optionsbox_bmp3.current(0)

        # Range Slider for Constraints
        self.sliderframe1 = MyRangeSliderFrame3(self)
        self.sliderframe1.grid(row=4, column=1, columnspan=2, sticky='w')

        # Range Slider for Constraints
        self.sliderframe2 = MyRangeSliderFrame3(self)
        self.sliderframe2.grid(row=5, column=1, columnspan=2, sticky='e')

    def clickallsnaptoticks(self, event=None):
        self.sliderframe1.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)
        self.sliderframe2.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist)

    def update_box_options(self, optinstance):
        print("additionalconstraints_frame:update_box_options: finding eligible parameters and their ya'adim...")
        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        optinstance.generate_emptyparametermatrices()
        optinstance.mark_eligibility()
