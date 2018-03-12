import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from gui.useframes.RangeSliderFrame import RangeSliderFrame


class AdditionalConstraintsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        """The frame to specify additional constraints/bounds on free parameters"""
        tk.Frame.__init__(self, parent, *args, **kwargs)  # Use superclass __init__ to create the actual frame
        self.parent = parent

        self.noconstraints_button = None

        self.__snapToTicksCheckVar = tk.IntVar()
        self.__snapToTicksCheckVar.set(int(0))
        self.__snapToTicks = None

        self.dropdown_bmps = None

        self.checkvar = tk.IntVar(value=1)
        self.bmpslider = None

        self.max_for_each_bmp = None

        self.create_subframes()

    def create_subframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        self.rowconfigure(0, minsize=40)

        self.grid_columnconfigure(1, weight=1)

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

        # Text Labels
        tk.Label(self, text="BMP List", anchor='e').grid(row=1, column=0, sticky=tk.E)
        # Drop Down Menu (BMP List)
        options_list = ["N/A"]
        self.dropdown_bmps = self.my_dropdown(options_list)
        self.dropdown_bmps.grid(row=1, column=1, sticky='we')
        self.dropdown_bmps.current(0)
        self.dropdown_bmps.bind("<<ComboboxSelected>>", self.bmp_selection_update)

    def bmp_selection_update(self, event=None):
        bmpname = self.dropdown_bmps.get()
        bmpmax = self.max_for_each_bmp[bmpname]

        if np.isnan(bmpmax):
            print('The max hard upper bound for the "%s" BMP is NaN, cannot draw a range slider!' % bmpname)
        elif bmpmax == 0:
            print('The max hard upper bound for the "%s" BMP is zero, cannot draw a range slider!' % bmpname)
        else:
            print('The max hard upper bound for the "%s" BMP is %s.' % (bmpname, str(bmpmax)))
            self.bmpslider.setUpperBound(bmpmax)
            self.bmpslider.setLowerBound(0)
            self.bmpslider.setLower(bmpmax * 0.25)
            self.bmpslider.setUpper(bmpmax * 0.75)
            self.bmpslider.setMajorTickSpacing(bmpmax / 5)
            self.bmpslider.setMinorTickSpacing(bmpmax / 20)

    def clickallsnaptoticks(self, event=None):
        #self.sliderframe1.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

        self.bmpslider.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist, state="readonly")

    def update_box_options(self, optinstance):
        """Populate the constraint frame with list of eligible bmps included in the OptInstance
        Args:
            optinstance (OptInstance):
        """
        print("additionalconstraints_frame:update_box_options: finding eligible parameters and their ya'adim...")

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        optinstance.generate_emptyparametermatrices()
        optinstance.mark_eligibility()
        optinstance.generate_boundsmatrices()

        eligiblematrix = optinstance.pmatrices['ndas'].eligibleparametermatrix
        hubmatrix = optinstance.pmatrices['ndas'].hardupperboundmatrix
        bmplist = eligiblematrix.columns.tolist()
        self.max_for_each_bmp = hubmatrix.max(axis=0)

        self.dropdown_bmps['values'] = ['Select BMP'] + bmplist
        self.dropdown_bmps.current(0)

        # Create a range slider for bmp
        tempmax = 100
        self.bmpslider = RangeSliderFrame(self,
                                          upperbound=tempmax, lowerbound=0,
                                          upper=tempmax * 0.75, lower=tempmax * 0.25,
                                          majortickspacing=tempmax / 5, minortickspacing=tempmax / 20,
                                          snaptoticks=False)
        self.bmpslider.grid(row=1, column=2, columnspan=2, sticky='w')

    def get_results(self):
        # Optmeta = namedtuple('freeparamgrps', 'agencies sectors')
        # self.results = Optmeta(agencies=self.agencydualbox.get_selection(),
        #                        sectors=self.sectordualbox.get_selection())
        # print('freeparamgrps results:')
        # print(self.results)
        # return self.results
        pass
