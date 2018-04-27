import pandas as pd
import os
from sandbox.util.decisionspace import DecisionSpace
from sandbox.util.scenariomaker.scenariomaker import ScenarioMaker
from sandbox.util.Examples import Examples
from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class OptCase(object):
    def __init__(self):
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
        self.decisionspace = DecisionSpace()
        # Queries to the source data
        self.jeeves = self.decisionspace.jeeves

        self.name = None
        self.description = None
        self.baseyear = None
        self.basecondname = None
        self.wastewatername = None
        self.costprofilename = None
        self.geoscalename = None
        self.geoareanames = None

        # Individual Components for metadata
        self.baseconditionid = pd.DataFrame(data=[1], columns=['baseconditionid'])
        # TODO: use real baseconditionid instead of this^ temporary placeholder

        # Scenarios
        self.scenarios_land = []
        self.scenarios_animal = []
        self.scenarios_manure = []

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

    def load_example(self, name=''):
        """ load pre-defined example metadata options for testing purposes

        Parameters:
            name (str):  this is the name of the example to load.

        """
        ex = Examples(name)

        self.name = ex.name
        self.description = ex.description
        self.baseyear = ex.baseyear
        self.basecondname = ex.basecondname
        self.wastewatername = ex.wastewatername
        self.costprofilename = ex.costprofilename
        self.geoscalename = ex.geoscalename
        self.geoareanames = ex.geoareanames

    def custom_scenario(self, scale='', areanames=''):
        ex = Examples('basenogeography')

        self.name = ex.name
        self.description = ex.description
        self.baseyear = ex.baseyear
        self.basecondname = ex.basecondname
        self.wastewatername = ex.wastewatername
        self.costprofilename = ex.costprofilename

        self.geoscalename = scale
        self.geoareanames = areanames

    def proceed_from_geography_to_decision_space(self):
        for dsname, ds in self.decisionspace:
            ds.proceed_from_geography_to_decision_space(scale=self.geoscalename,
                                                        areanames=self.geoareanames)

    def proceed_from_geoagencysectorids_to_decision_space(self):
        for dsname, ds in self.decisionspace:
            ds.proceed_from_geoagencysectorids_to_decision_space(scale=self.geoscalename,
                                                                 areanames=self.geoareanames)

    # hooks for graphical interface get/put
    def populate_geography_from_scale_and_areas(self):
        for dsname, ds in self.decisionspace:
            ds.populate_geography_from_scale_and_areas(scale=self.geoscalename,
                                                       areanames=self.geoareanames)

    def set_metadata(self, metadata_results):
        self.name = metadata_results.name
        self.description = metadata_results.description
        self.baseyear = metadata_results.baseyear
        self.basecondname = metadata_results.basecond
        self.wastewatername = metadata_results.wastewater
        self.costprofilename = metadata_results.costprofile
        self.geoscalename = metadata_results.scale
        self.geoareanames = metadata_results.area  # For Counties, this is in the form of "[County], [StateAbbeviation]"

    def set_freeparamgrps(self, freeparamgrp_results):
        for dsname, ds in self.decisionspace:
            ds.set_freeparamgrps(agencycodes=freeparamgrp_results.agencies,
                                 sectornames=freeparamgrp_results.sectors)

    # Generating scenario(s) from the decision space
    def generate_scenario(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        # TODO: code this (randomization for each variable, and then writing to file)
        scenario = ScenarioMaker(decisionspace=self.decisionspace).single

        if scenariotype == 'random':
            scenario.randomize_betweenbounds()
        else:
            scenario.randomize_betweenbounds()

        # Scenario is written to file.
        self.scenarios_land[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land.txt'),
                                       sep='\t', header=True, index=False, line_terminator='\r\n')
        self.scenarios_animal[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal.txt'),
                                         sep='\t', header=True, index=False, line_terminator='\r\n')
        self.scenarios_manure[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure.txt'),
                                         sep='\t', header=True, index=False, line_terminator='\r\n')

    def generate_multiple_scenarios(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        population = ScenarioMaker(decisionspace=self.decisionspace).population

        if scenariotype == 'hypercube':
            population.generate_latinhypercube()
        else:
            population.generate_latinhypercube()

        # columns that are ids are translated to names, and scenarios are written to file.
        i = 0
        for df in population.scenarios_land:
            self.scenarios_land.append(self.decisionspace.land.nametable)
            self.scenarios_land[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land_%d.txt' % i),
                                           sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_animal:
            self.scenarios_animal.append(self.dsanimal.nametable)
            self.scenarios_animal[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_manure:
            self.scenarios_manure.append(self.queries.translate_sftabidtable_to_sftabnametable(sftabidtable=df))
            self.scenarios_manure[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1
