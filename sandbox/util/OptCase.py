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

        self.name = name
        self.description = description
        self.baseyear = baseyear
        self.basecondname = basecondname
        self.wastewatername = wastewatername
        self.costprofilename = costprofilename
        self.geoscalename = geoscalename
        self.geoareanames = geoareanames

        # Individual Components for metadata
        self.baseconditionid = None
        # self.baseconditionid = pd.DataFrame(data=[3], columns=['baseconditionid'])

        # Scenarios
        self.scenarios = None

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

    @classmethod
    def blank(cls):
        """ Constructor to generate an empty OptCase
        """
        # Decision Space
        cls.decisionspace = DecisionSpace.blank()
        # Queries to the source data
        cls.jeeves = cls.decisionspace.jeeves
        return cls()

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

    def set_decisionspace_agencies_and_sectors(self, agencycodes=None, sectornames=None):
        self.decisionspace.set_freeparamgrps(agencycodes=agencycodes, sectornames=sectornames)

    def __generate_decisionspace_using_case_geography(self):
        # Decision Space
        self.decisionspace = DecisionSpace.blank()
        # Queries to the source data
        self.jeeves = self.decisionspace.jeeves
        # Metadata Component
        self.baseconditionid = self.decisionspace.set_baseconditionid_from_yearname(year=self.baseyear,
                                                                                    name=self.basecondname)
        self.decisionspace = DecisionSpace.fromgeo(scale=self.geoscalename,
                                                   areanames=self.geoareanames,
                                                   baseconditionid=self.baseconditionid)

    # hooks for graphical interface get/put
    def generate_decision_space_using_case_geoagencysectorids(self):
        self.baseconditionid = self.decisionspace.set_baseconditionid_from_yearname(year=self.baseyear,
                                                                                    name=self.basecondname)
        self.decisionspace.proceed_to_decision_space_from_geoagencysectorids()

    # Generating scenario(s) from the decision space
    def generate_scenarios_from_decisionspace(self, scenariotype='hypercube', n='population'):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """

        print('OptCase.generate_scenarios_from_decisionspace():')
        print(self.baseconditionid)

        if n == 'single':
            self.scenarios = ScenarioMaker(decisionspace=self.decisionspace).single
        elif n == 'population':
            self.scenarios = ScenarioMaker(decisionspace=self.decisionspace).population

        if scenariotype == 'random':
            self.scenarios.randomize_betweenbounds()
        elif scenariotype == 'hypercube':
            self.scenarios.generate_latinhypercube()
        else:
            self.scenarios.randomize_betweenbounds()

        # Add Any extra info columns to the output
        self.scenarios.add_bmptype_column(jeeves=self.jeeves)

        self.scenarios.write_to_tab_delimited_txt_file()
