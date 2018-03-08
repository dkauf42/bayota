import tkinter as tk
import tkinter.ttk as ttk
from gui.useframes.RangeSliderFrame import RangeSliderFrame


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

        self.bmpButtonList = []
        self.bmpSliderList = []

        self.create_subframes()

    def create_subframes(self):
        self.columnconfigure(0, minsize=50)
        self.columnconfigure(1, minsize=100)
        self.columnconfigure(2, minsize=10)
        self.rowconfigure(0, minsize=40)

        self.grid_columnconfigure(1, weight=1)

        # # Text Labels
        # tk.Label(self, text="BMP #1", anchor='e').grid(row=1, column=0, sticky=tk.E)
        # tk.Label(self, text="BMP #2", anchor="e").grid(row=2, column=0, sticky=tk.E)
        # tk.Label(self, text="BMP #3", anchor='e').grid(row=3, column=0, sticky=tk.E)

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

        # # Drop Down Menu
        # options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        # self.optionsbox_bmp1 = self.my_dropdown(options_list)
        # self.optionsbox_bmp1.grid(row=1, column=1, sticky='we')
        # self.optionsbox_bmp1.current(0)
        #
        # # Drop Down Menu
        # options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        # self.optionsbox_bmp2 = self.my_dropdown(options_list)
        # self.optionsbox_bmp2.grid(row=2, column=1, sticky='we')
        # self.optionsbox_bmp2.current(0)
        #
        # # Drop Down Menu
        # options_list = ["0%", "20%", "40%", "60%", "80%", "100%"]
        # self.optionsbox_bmp3 = self.my_dropdown(options_list)
        # self.optionsbox_bmp3.grid(row=3, column=1, sticky='we')
        # self.optionsbox_bmp3.current(0)

        # # Range Slider for Constraints
        # self.sliderframe1 = RangeSliderFrame(self)
        # self.sliderframe1.grid(row=4, column=1, columnspan=2, sticky='w')
        #
        # # Range Slider for Constraints
        # self.sliderframe2 = RangeSliderFrame(self)
        # self.sliderframe2.grid(row=5, column=1, columnspan=2, sticky='e')

    def clickallsnaptoticks(self, event=None):
        #self.sliderframe1.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)
        #self.sliderframe2.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)
        for slider in self.bmpSliderList:
            slider.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

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

        print('additionalconstraints_frame.update_box_options(): eligible matrix SUMs:')
        print(eligiblematrix.sum(axis=0))

        max_for_each_bmp = hubmatrix.max(axis=0)
        print('additionalconstraints_frame.update_box_options(): eligible matrix MAXs:')
        print(max_for_each_bmp)

        print('Additionconstraints_frame.update_box_options: bmplist...')
        print(bmplist)

        for i in range(5):
            print(i)
            bmpname = bmplist[i]
            bmpmax = max_for_each_bmp[bmpname]

            # Create button for each bmp
            newbutton = tk.Button(self, text=bmpname,
                                  command=lambda j=i + 1: self.bmpButtonCallback(j))
            newbutton.grid(row=1+i, column=0, columnspan=1, sticky='w')
            self.bmpButtonList.append(newbutton)

            # Create a range slider for each bmp
            newslider = RangeSliderFrame(self,
                                         upperbound=bmpmax, lowerbound=0,
                                         upper=bmpmax*0.75, lower=bmpmax*0.25,
                                         majortickspacing=bmpmax/5, minortickspacing=bmpmax/20,
                                         snaptoticks=False)
            newslider.grid(row=1+i, column=1, columnspan=2, sticky='w')
            self.bmpSliderList.append(newslider)

        # def update_box_options(self, queries=None, optinstance=None):
        #
        #     mylist = queries.base.get_agencies_in_lrsegs(lrsegs=optinstance.geographies_included['LandRiverSegment'])
        #
        #     self.agencydualbox.set_new_left_side_items(mylist)
        #
        #     mylist = queries.source.get_all_sector_names()
        #     self.sectordualbox.set_new_left_side_items(mylist)

    def bmpButtonCallback(self, btnID):
        print('Additional_constraints_frame.bmpButtonCallback: btnID is <%s>' % btnID)
        pass
