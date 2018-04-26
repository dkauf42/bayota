import pandas as pd
import os
from sandbox.util.DecisionSpaces import LandDecisionSpace, AnimalDecisionSpace, ManureDecisionSpace
from sandbox.util.ScenarioMaker import ScenarioMaker
from sandbox.util.PopulationMaker import PopulationMaker
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

        # Decision Spaces
        self.dsland = None
        self.dsanimal = None
        self.dsmanure = None

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
                       "# of lrsegs:              %s\n" \
                       "agencies included:        %s\n" \
                       "sectors included:         %s\n" \
                       "************************************\n" %\
                       tuple([str(i) for i in [d['name'],
                                               d['description'],
                                               d['baseyear'],
                                               d['basecondname'],
                                               d['wastewatername'],
                                               d['costprofilename'],
                                               d['geoscalename'],
                                               d['geoareanames'],
                                               d['lrsegids'].shape[0],
                                               d['agencyids'],
                                               d['sectorids']
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

    def generate_decisionspaces(self):
        self.dsland = LandDecisionSpace()
        self.dsanimal = AnimalDecisionSpace()
        self.dsmanure = ManureDecisionSpace()

    # hooks for graphical interface get/put
    def populate_geography_from_scale_and_areas(self):
        self.dsland.populate_geography_from_scale_and_areas(scale=self.geoscalename, areanames=self.geoareanames)
        self.dsanimal.populate_geography_from_scale_and_areas(scale=self.geoscalename, areanames=self.geoareanames)
        self.dsmanure.populate_geography_from_scale_and_areas(scale=self.geoscalename, areanames=self.geoareanames)

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
        self.dsland.set_freeparamgrps(agencycodes=freeparamgrp_results.agencies,
                                      sectornames=freeparamgrp_results.sectors)
        self.dsanimal.set_freeparamgrps(agencycodes=freeparamgrp_results.agencies,
                                        sectornames=freeparamgrp_results.sectors)
        self.dsmanure.set_freeparamgrps(agencycodes=freeparamgrp_results.agencies,
                                        sectornames=freeparamgrp_results.sectors)

    # Generating scenario(s) from the decision space
    def generate_scenario(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        # TODO: code this (randomization for each variable, and then writing to file)
        scenario = ScenarioMaker()
        scenario.initialize_from_decisionspace(land=self.dsland.idtable,
                                               animal=self.dsanimal.idtable,
                                               manure=self.dsmanure.idtable)

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
        population = PopulationMaker()
        population.initialize_from_decisionspace(land=self.land_decisionspace,
                                                 animal=self.animal_decisionspace,
                                                 manure=self.manure_decisionspace)

        if scenariotype == 'hypercube':
            population.generate_latinhypercube()
        else:
            population.generate_latinhypercube()

        # columns that are ids are translated to names, and scenarios are written to file.
        i = 0
        for df in population.scenarios_land:
            self.scenarios_land.append(self.queries.translate_slabidtable_to_slabnametable(slabidtable=df))
            self.scenarios_land[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land_%d.txt' % i),
                                           sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_animal:
            self.scenarios_animal.append(self.queries.translate_scabidtable_to_scabnametable(scabidtable=df))
            self.scenarios_animal[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_manure:
            self.scenarios_manure.append(self.queries.translate_sftabidtable_to_sftabnametable(sftabidtable=df))
            self.scenarios_manure[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1
