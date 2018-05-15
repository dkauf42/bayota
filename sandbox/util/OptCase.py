import pandas as pd
from sandbox.util.decisionspace import DecisionSpace
from sandbox.util.scenariomaker.scenariomaker import ScenarioMaker
from sandbox.util.Examples import Examples
from sandbox.__init__ import get_outputdir
from sandbox import settings

writedir = get_outputdir()


class OptCase(object):
    def __init__(self, name=None, description=None, baseyear=None, basecondname=None,
                 wastewatername=None, costprofilename=None, geoscalename=None, geoareanames=None):
        """ Base class for all optimization Cases.
        Represents the options and subset of data necessary for conducting a particular optimization run

        A Case holds:
            - metadata fields
            - constraints
            - and the decision space.
        A Case can perform these actions:
            - load an example
            - generate scenarios

        """
        self.logtostdout = False
        self.successful_creation_log = False

        # Decision Space
        self.decisionspace = DecisionSpace.blank()
        # Queries to the source data
        self.jeeves = self.decisionspace.jeeves

        self.name = name
        self.description = description
        self.baseyear = baseyear
        self.basecondname = basecondname
        self.wastewatername = wastewatername
        self.costprofilename = costprofilename
        self.geoscalename = geoscalename
        self.geoareanames = geoareanames

        # Individual Components for metadata
        # self.baseconditionid = None
        self.baseconditionid = pd.DataFrame(data=[3], columns=['baseconditionid'])
        # TODO: use real baseconditionid instead of this^ temporary placeholder

        # Scenarios
        self.scenarios_land = []
        self.scenarios_animal = []
        self.scenarios_manure = []

        if geoscalename is not None:
            self.__generate_decisionspace_using_case_geography()

    @classmethod
    def loadexample(cls, name=''):
        """ Constructor to generate an OptCase from a metadata example set
        load pre-defined example metadata options for testing purposes

        Parameters:
            name (str):  this is the name of the example to load.
        """
        if settings.verbose:
            print('** OptCase is loading example "%s" **  {OptCase.loadexample()}' % name)

        ex = Examples(name)

        return cls(name=ex.name, description=ex.description, baseyear=ex.baseyear, basecondname=ex.basecondname,
                   wastewatername=ex.wastewatername, costprofilename=ex.costprofilename,
                   geoscalename=ex.geoscalename, geoareanames=ex.geoareanames)

    @classmethod
    def loadcustom(cls, scale='', areanames=''):
        """ Constructor to generate an OptCase with input arguments: scale and a list of areanames

        Parameters:
            scale (str):
            areanames (list of str):
        """
        ex = Examples('basenogeography')

        return cls(name=ex.name, description=ex.description, baseyear=ex.baseyear, basecondname=ex.basecondname,
                   wastewatername=ex.wastewatername, costprofilename=ex.costprofilename,
                   geoscalename=scale, geoareanames=areanames)

    def __repr__(self):
        """ Custom 'print' that displays the metadata defined for this OptCase.
        """
        d = self.__dict__

        formattedstr = "\n***** OptCase Details *****\n" \
                       "name:                     %s\n" \
                       "description:              %s\n" \
                       "base year:                %s\n" \
                       "base condition:           %s\n" \
                       "wastewater:               %s\n" \
                       "cost profile:             %s\n" \
                       "geographic scale:         %s\n" \
                       "geographic areas:         %s\n" \
                       "deicisionspace:           %s\n" \
                       "************************************\n" %\
                       tuple([str(i) for i in [d['name'],
                                               d['description'],
                                               d['baseyear'],
                                               d['basecondname'],
                                               d['wastewatername'],
                                               d['costprofilename'],
                                               d['geoscalename'],
                                               d['geoareanames'],
                                               d['decisionspace'].__dict__
                                               ]
                              ])

        return formattedstr

    # Setters
    def set_metadata_to_example(self, name=''):
        """ load pre-defined example metadata options for testing purposes

        Parameters:
            name (str):  this is the name of the example to load.

        """
        if settings.verbose:
            print('** OptCase is loading example "%s" **  {OptCase.loadexample()}' % name)

        ex = Examples(name)

        self.set_metadata(name=ex.name, description=ex.description, baseyear=ex.baseyear, basecondname=ex.basecondname,
                          wastewatername=ex.wastewatername, costprofilename=ex.costprofilename,
                          geoscalename=ex.geoscalename, geoareanames=ex.geoareanames)

    def set_metadata(self, name=None, description=None, baseyear=None, basecondname=None,
                     wastewatername=None, costprofilename=None, geoscalename=None, geoareanames=None):
        self.name = name
        self.description = description
        self.baseyear = baseyear
        self.basecondname = basecondname
        self.wastewatername = wastewatername
        self.costprofilename = costprofilename
        self.geoscalename = geoscalename
        self.geoareanames = geoareanames  # For Counties, this is in the form of "[County], [StateAbbeviation]"

        self.__generate_decisionspace_using_case_geography()
        # self.set_decisionspace_geography()

    # def set_decisionspace_geography(self):
    #     self.decisionspace.set_geography_from_scale_and_areas(scale=self.geoscalename,
    #                                                           areanames=self.geoareanames)

    def set_decisionspace_agencies_and_sectors(self, agencycodes=None, sectornames=None):
        self.decisionspace.set_freeparamgrps(agencycodes=agencycodes, sectornames=sectornames)

    def __generate_decisionspace_using_case_geography(self):
        self.decisionspace = DecisionSpace.fromgeo(scale=self.geoscalename,
                                                   areanames=self.geoareanames,
                                                   baseconditionid=self.baseconditionid)

    # hooks for graphical interface get/put
    def generate_decision_space_using_case_geoagencysectorids(self):
        self.decisionspace.set_baseconditionid_from_name(name=self.basecondname)
        self.decisionspace.proceed_to_decision_space_from_geoagencysectorids()

    # Generating scenario(s) from the decision space
    def generate_single_scenario(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        # TODO: code this (randomization for each variable, and then writing to file)
        scenario = ScenarioMaker(decisionspace=self.decisionspace).single

        if scenariotype == 'random':
            scenario.randomize_betweenbounds()
        else:
            scenario.randomize_betweenbounds()

        # add scenarios to OptCase attribute
        for scenariotype, scenarios in scenario:
            for df in scenarios:
                if scenariotype == 'animal':
                    self.scenarios_animal.append(df)
                if scenariotype == 'land':
                    self.scenarios_land.append(df)
                if scenariotype == 'manure':
                    self.scenarios_manure.append(df)

        scenario.write_to_tab_delimited_txt_file()

    def generate_multiple_scenarios(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        population = ScenarioMaker(decisionspace=self.decisionspace).population

        # Generate scenarios
        if scenariotype == 'hypercube':
            population.generate_latinhypercube()
        else:
            population.generate_latinhypercube()

        # add scenarios to OptCase attribute
        for scenariotype, scenarios in population:
            for df in scenarios:
                if scenariotype == 'animal':
                    self.scenarios_animal.append(df)
                if scenariotype == 'land':
                    self.scenarios_land.append(df)
                if scenariotype == 'manure':
                    self.scenarios_manure.append(df)

        for i in range(len(population.scenarios_animal)):
            population.scenarios_animal[i] = self.jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(population.scenarios_animal[i])
        for i in range(len(population.scenarios_land)):
            population.scenarios_land[i] = self.jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(population.scenarios_land[i])
        for i in range(len(population.scenarios_manure)):
            population.scenarios_manure[i] = self.jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(population.scenarios_manure[i])

        population.write_to_tab_delimited_txt_file()
