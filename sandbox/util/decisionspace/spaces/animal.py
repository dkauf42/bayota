import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Animal(Space):
    def __init__(self, jeeves=None):
        """ Animal Decision Space

        the idtable for animal is characterized as a 'scab' table, i.e.
        S(ource), C(ounty), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.\
            animal_scabidtable_from_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.source_county_agency_table,
                                                              baseconditionid=self.baseconditionid)
        # Translate to names
        self.nametable = self.jeeves.translator.\
            translate_scabidtable_to_scabnametable(self.idtable)

    def qc(self):
        pass

    def append_bounds(self):
        self.idtable['lowerbound'] = 0
        self.idtable['upperbound'] = 100
        # For Animals: Add...?
        return self.idtable.copy()
        # self.animal_decisionspace = self.queries.\
        #     appendBounds_to_animal_scabidtable(scabidtable=self.animal_scabidtable)

