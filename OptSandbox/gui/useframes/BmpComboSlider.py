import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from copy import deepcopy
from gui.useframes.RangeSliderFrame import RangeSliderFrame


class BmpComboSlider(tk.Frame):
    def __init__(self, parent,
                 dropdownlist=None,
                 maxs_dict=None,
                 mins_dict=None):
        """Two side-by-side listboxes are created with which items can be moved from one to the other"""
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.maxs_dict = maxs_dict
        self.mins_dict = mins_dict

        # The input list is checked for duplicate values.

        # Drop Down Menu (BMP List)
        self.dropdown_bmps = self.my_dropdown(dropdownlist)
        self.dropdown_bmps.grid(row=1, column=1, sticky='we')
        self.dropdown_bmps.current(0)
        self.dropdown_bmps.bind("<<ComboboxSelected>>", self.bmp_selection_update)

        self.last_bmp = str(self.dropdown_bmps.get())

        # use deepcopy to create user dictionaries that are not referencing same max/min dictionary objects
        self.user_max_for_each_bmp = deepcopy(self.maxs_dict)
        self.user_min_for_each_bmp = deepcopy(self.mins_dict)
        self.bmp_bounds_set = dict((k, 0) for k in list(self.maxs_dict.keys()))  # initialized with zeros

        # Create a range slider for bmp
        tempmax = 100
        self.bmpslider = RangeSliderFrame(self,
                                          upperbound=tempmax, lowerbound=0,
                                          upper=tempmax * 0.75, lower=tempmax * 0.25,
                                          majortickspacing=tempmax / 5, minortickspacing=tempmax / 20,
                                          snaptoticks=False)
        self.bmpslider.grid(row=1, column=2, columnspan=2, sticky='w')

    def my_dropdown(self, optionslist):
        variable = tk.StringVar(self)
        return ttk.Combobox(self, textvariable=variable, values=optionslist, state="readonly")

    def snapToTicksCheck_onClick(self, var=None):
        self.bmpslider.snapToTicksCheck_onClick(var=var)

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
            bmpmax = self.maxs_dict[new_bmpname]
            bmpmin = self.mins_dict[new_bmpname]
            user_bmpmax = self.user_max_for_each_bmp[new_bmpname]
            user_bmpmin = self.user_min_for_each_bmp[new_bmpname]
            if np.isnan(bmpmax):
                # Don't update
                print('The max hard upper bound for the "%s" BMP is NaN, cannot draw a range slider!' % new_bmpname)
                self.bmpslider.setLower(0)
                self.bmpslider.setUpper(0)
            else:
                print('- bounds for "%s" are hlb=[%d], hub=[%d], usermin=[%d], usermax=[%d].' %
                      (new_bmpname, bmpmin, bmpmax, user_bmpmin, user_bmpmax))

                if bmpmax == 0:
                    # Don't update
                    print('The max hard upper bound for the "%s" BMP is zero,'
                          'cannot draw a range slider!' % new_bmpname)
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
                        print('-- setting the carets to previously user defined values:'
                              'upperCaret=[%d], lowerCaret=[%d]' % (user_bmpmax, user_bmpmin))
                        self.bmpslider.setLower(user_bmpmin)
                        self.bmpslider.setUpper(user_bmpmax)

                    self.last_bmp = new_bmpname
