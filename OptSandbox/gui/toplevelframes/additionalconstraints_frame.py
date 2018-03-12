import tkinter as tk
import tkinter.ttk as ttk
import numpy as np
from copy import deepcopy
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
        self.bmpslider = None

        self.last_bmp = ''
        self.checkvar = tk.IntVar(value=1)

        self.max_for_each_bmp = None
        self.min_for_each_bmp = None
        self.user_max_for_each_bmp = None
        self.user_min_for_each_bmp = None
        self.bmp_bounds_set = {}

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
        new_bmpname = self.dropdown_bmps.get()
        print("\n** Changed BMP from <%s> to <%s>: " % (self.last_bmp, new_bmpname))

        # Save previous slider values here, before any updates
        last_lower = self.bmpslider.getLower()
        last_upper = self.bmpslider.getUpper()
        self.user_max_for_each_bmp[self.last_bmp] = last_upper
        self.user_min_for_each_bmp[self.last_bmp] = last_lower
        self.bmp_bounds_set[self.last_bmp] = 1
        print('- saving "%s" user bounds: lower=[%d] and upper=[%d]' %
              (self.last_bmp, last_lower, last_upper))

        # Update slider with new values
        if new_bmpname == 'Select BMP':
            # Don't update the slider if the prompt is selected
            pass
        else:
            bmpmax = self.max_for_each_bmp[new_bmpname]
            bmpmin = self.min_for_each_bmp[new_bmpname]
            user_bmpmax = self.user_max_for_each_bmp[new_bmpname]
            user_bmpmin = self.user_min_for_each_bmp[new_bmpname]
            print('- bounds for "%s" are hlb=[%d], hub=[%d], usermin=[%d], usermax=[%d].' %
                  (new_bmpname, bmpmin, bmpmax, user_bmpmin, user_bmpmax))
            if np.isnan(bmpmax):
                # Don't update
                print('The max hard upper bound for the "%s" BMP is NaN, cannot draw a range slider!' % new_bmpname)
                self.bmpslider.setLower(0)
                self.bmpslider.setUpper(0)
            elif bmpmax == 0:
                # Don't update
                print('The max hard upper bound for the "%s" BMP is zero, cannot draw a range slider!' % new_bmpname)
                self.bmpslider.setLower(0)
                self.bmpslider.setUpper(0)
            else:
                # Update!
                print('Updating Slider!')
                print('-- setting LowerBound=[%d], UpperBound=[%d]' % (0, bmpmax))
                self.bmpslider.setLowerBound(0)
                self.bmpslider.setUpperBound(bmpmax)
                self.bmpslider.setMajorTickSpacing(bmpmax / 5)
                self.bmpslider.setMinorTickSpacing(bmpmax / 20)

                if self.bmp_bounds_set[new_bmpname] == 0:
                    # Update slider with default values from max
                    print('-- setting Carets to defaults: lowerCaret=[%d], upperCaret=[%d]' %
                          (bmpmax * 0.25, bmpmax * 0.75))
                    self.bmpslider.setLower(bmpmax * 0.25)
                    self.bmpslider.setUpper(bmpmax * 0.75)
                else:
                    # Update slider with previously set user values
                    print('-- setting the carets to previously user defined values: upperCaret=[%d], lowerCaret=[%d]' %
                          (user_bmpmax, user_bmpmin))
                    self.bmpslider.setLower(user_bmpmin)
                    self.bmpslider.setUpper(user_bmpmax)

                self.last_bmp = new_bmpname

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

        self.max_for_each_bmp = optinstance.pmatrices['ndas'].get_list_of_max_hubs_for_bmps()
        self.min_for_each_bmp = optinstance.pmatrices['ndas'].get_list_of_min_hlbs_for_bmps()
        # use deepcopy to create user dictionaries that are not referencing same max/min dictionary objects
        self.user_max_for_each_bmp = deepcopy(self.max_for_each_bmp)
        self.user_min_for_each_bmp = deepcopy(self.min_for_each_bmp)
        self.bmp_bounds_set = dict((k, 0) for k in list(self.max_for_each_bmp.keys()))  # initialized with zeros

        self.dropdown_bmps['values'] = ['Select BMP'] + optinstance.pmatrices['ndas'].get_list_of_bmps()
        self.dropdown_bmps.current(0)
        self.last_bmp = str(self.dropdown_bmps.get())

        # Create a range slider for bmp
        tempmax = 100
        self.bmpslider = RangeSliderFrame(self,
                                          upperbound=tempmax, lowerbound=0,
                                          upper=tempmax * 0.75, lower=tempmax * 0.25,
                                          majortickspacing=tempmax / 5, minortickspacing=tempmax / 20,
                                          snaptoticks=False)
        self.bmpslider.grid(row=1, column=2, columnspan=2, sticky='w')

    def clickallsnaptoticks(self, event=None):
        self.bmpslider.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist, state="readonly")

    def get_results(self):
        # Optmeta = namedtuple('freeparamgrps', 'agencies sectors')
        # self.results = Optmeta(agencies=self.agencydualbox.get_selection(),
        #                        sectors=self.sectordualbox.get_selection())
        # print('freeparamgrps results:')
        # print(self.results)
        # return self.results
        pass
