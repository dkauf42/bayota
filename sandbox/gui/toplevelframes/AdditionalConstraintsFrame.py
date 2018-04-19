import tkinter as tk
from sandbox.gui.useframes.BmpComboSlider import BmpComboSlider


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

        self.bmpcomboslider_land = None
        self.bmpcomboslider_animal = None
        self.bmpcomboslider_manure = None

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
        tk.Label(self, text="Land BMPs", anchor='e').grid(row=1, column=0, sticky=tk.E)
        tk.Label(self, text="Animal BMPs", anchor='e').grid(row=2, column=0, sticky=tk.E)
        tk.Label(self, text="Manure BMPs", anchor='e').grid(row=3, column=0, sticky=tk.E)

    def update_box_options(self, optcase):
        """Populate the constraint frame with list of eligible bmps included in the OptCase
        Args:
            optcase (OptCase):
        """
        # Generate the decision space
        optcase.proceed_from_geoagencysectorids_to_decision_space()

        # Create Dropdown and Range Sliders (Land)
        land_table = optcase.land_slabidtable.drop_duplicates(subset=['bmpid'])
        list_of_bmps = optcase.queries.bmpnames_from_bmpids(bmpids=land_table['bmpid']).bmpshortname.tolist()
        list_of_max_hubs_for_bmps = dict(zip(list_of_bmps, land_table['upperbound'].tolist()))
        list_of_min_hlbs_for_bmps = dict(zip(list_of_bmps, land_table['lowerbound'].tolist()))
        self.bmpcomboslider_land = BmpComboSlider(self,
                                                  dropdownlist=['Select BMP'] + list_of_bmps,
                                                  maxs_dict=list_of_max_hubs_for_bmps,
                                                  mins_dict=list_of_min_hlbs_for_bmps)
        self.bmpcomboslider_land.grid(row=1, column=1, columnspan=3, sticky='we')
        # (Animal)
        animal_table = optcase.animal_scabidtable.drop_duplicates(subset=['bmpid'])
        list_of_bmps = optcase.queries.bmpnames_from_bmpids(bmpids=animal_table['bmpid']).bmpshortname.tolist()
        list_of_max_hubs_for_bmps = dict(zip(list_of_bmps, animal_table['upperbound'].tolist()))
        list_of_min_hlbs_for_bmps = dict(zip(list_of_bmps, animal_table['lowerbound'].tolist()))
        self.bmpcomboslider_animal = BmpComboSlider(self,
                                                    dropdownlist=['Select BMP'] + list_of_bmps,
                                                    maxs_dict=list_of_max_hubs_for_bmps,
                                                    mins_dict=list_of_min_hlbs_for_bmps)
        self.bmpcomboslider_animal.grid(row=2, column=1, columnspan=3, sticky='we')
        # (Manure)
        manure_table = optcase.manure_sftabidtable.drop_duplicates(subset=['bmpid'])
        list_of_bmps = optcase.queries.bmpnames_from_bmpids(bmpids=manure_table['bmpid']).bmpshortname.tolist()
        list_of_max_hubs_for_bmps = dict(zip(list_of_bmps, manure_table['upperbound'].tolist()))
        list_of_min_hlbs_for_bmps = dict(zip(list_of_bmps, manure_table['lowerbound'].tolist()))
        self.bmpcomboslider_manure = BmpComboSlider(self,
                                                    dropdownlist=['Select BMP'] + list_of_bmps,
                                                    maxs_dict=list_of_max_hubs_for_bmps,
                                                    mins_dict=list_of_min_hlbs_for_bmps)
        self.bmpcomboslider_manure.grid(row=3, column=1, columnspan=3, sticky='we')

    def clickallsnaptoticks(self, event=None):
        self.bmpcomboslider_land.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)
        self.bmpcomboslider_animal.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)
        self.bmpcomboslider_manure.snapToTicksCheck_onClick(var=self.__snapToTicksCheckVar)

    def get_results(self):
        # Optmeta = namedtuple('freeparamgrps', 'agencies sectors')
        # self.results = Optmeta(agencies=self.agencydualbox.get_selection(),
        #                        sectors=self.sectordualbox.get_selection())
        # print('freeparamgrps results:')
        # print(self.results)
        # return self.results
        pass
