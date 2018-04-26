from .decisionspace import DecisionSpace
from sandbox import settings


class AnimalDecisionSpace(DecisionSpace):
    def __init__(self):
        DecisionSpace.__init__(self)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.animal_scabidtable = self.jeeves.bmp.\
            animal_scabidtable_from_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.source_county_agency_table,
                                                              baseconditionid=self.baseconditionid)
        # Translate to names
        self.animal_scabnametable = self.jeeves.translator.\
            translate_scabidtable_to_scabnametable(self.animal_scabidtable)

    def qc(self):
        pass

    def append_bounds(self):
        self.scabidtable['lowerbound'] = 0
        self.scabidtable['upperbound'] = 100
        # For Animals: Add...?
        return self.scabidtable.copy()
        # self.animal_decisionspace = self.queries.\
        #     appendBounds_to_animal_scabidtable(scabidtable=self.animal_scabidtable)

