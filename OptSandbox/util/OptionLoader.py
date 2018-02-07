import pandas as pd


class OptionLoader:
    def __init__(self, optionsfile='', srcdataobj=None):
        """Load an 'options' file that represents the user choices for a particular scenario

        Parameters:
            optionsfile (str): file path of the 'options' csv file for the user scenario
            srcdataobj (obj): a SourceData object

        Attributes:
            options (pandas dataframe): values specified in the options file
            headers (list): names of each type of option (headers in the options file)

        Note:
            The options file should have the following columns:
            [BaseCondition,LandRiverSegment,CountyName,StateAbbreviation,
            StateBasin,OutOfCBWS,AgencyCode]

            Any blank options should be left fully blank

        """
        self.srcdataobj = srcdataobj
        self.options = pd.read_table(optionsfile, sep=',', header=0)
        self.headers = list(self.options.columns.values)

        self._validateoptions()  # check to make sure options are present in the Source Data or BaseCondition files
        print('<Option Validation and Loading Complete>')

    def _validateoptions(self):
        """Check that the options specified are valid"""
        oh = self.headers
        # headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
        #           OutOfCBWS, AgencyCode, Sector

        for h in oh:
            optionscolumn = self.options[h]
            if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
                # these are always valid options
                # TODO: include checks for 'all' and null options
                pass
            else:
                vo = self.validoptions(h)
                if ~optionscolumn.dropna().isin(vo).all():
                    raise LookupError('An option specified in the "%s" column of the options file is unrecognized' % h)

    def validoptions(self, argument):
        """Get list of valid option names to be specified for a particular option type"""
        switcher = {
                    'BaseCondition': "zero",  # TODO: include checks for valid basecondition options?
                    'LandRiverSegment': self.srcdataobj.getallnames('LandRiverSegment'),
                    'CountyName': self.srcdataobj.getallnames('CountyName'),
                    'StateAbbreviation': self.srcdataobj.getallnames('StateAbbreviation'),
                    'StateBasin': self.srcdataobj.getallnames('StateBasin'),
                    'OutOfCBWS': ('N', 'Y'),
                    'AgencyCode': self.srcdataobj.getallnames('AgencyCode'),
                    'Sector': self.srcdataobj.getallnames('Sector')
                   }
        return switcher[argument]
