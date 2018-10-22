import logging
import pandas as pd
from .spaces import Space

logger = logging.getLogger(__name__)

class Manure(Space):
    def __init__(self, jeeves=None, baseconditionid=None,
                 lrsegids=None, countyids=None, agencyids=None, sectorids=None,
                 lrseg_agency_table=None, source_lrseg_agency_table=None, source_county_agency_table=None):
        """ Manure Decision Space

        the idtable for manure is characterized as a 'sftab' table, i.e.
        S(ource), F(rom-FIPS), T(o-FIPS), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves, baseconditionid=baseconditionid,
                       lrsegids=lrsegids, countyids=countyids,
                       agencyids=agencyids, sectorids=sectorids,
                       lrseg_agency_table=lrseg_agency_table, source_lrseg_agency_table=source_lrseg_agency_table,
                       source_county_agency_table=source_county_agency_table)

    def append_bmps_to_SourceGeoAgencytable(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.append_manure_bmpids(SourceFromToAgencyIDtable=self.source_county_agency_table,
                                                            baseconditionid=self.baseconditionid)

    def translate_ids_to_names(self):
        # Translate to names
        self.nametable = self.jeeves.translator.translate_sftabidtable_to_sftabnametable(self.idtable)

    def qc_bmps(self):
        """ Remove LoadSources or BMPs that the optimization engine should not modify

        The following LoadSources are removed from the decision space:
        - AllLoadSources
        - "FEEDPermitted" and "FEEDNonPermitted" are removed; replaced by "FEED"

        """
        logger.debug('\t-- QC\'ing the idtable { in manure.qc_bmps() }, which looks like:')
        logger.debug(self.idtable.head())
        logger.debug('^shape is %s' % (self.idtable.shape, ))

        origrowcnt, origcolcnt = self.idtable.shape
        newtable = self.idtable

        removaltotal = 0

        singlebmpstoremove = ['MTT19',  # "Manure Treatment Direct Monitor"
                              ]

        for bmpnametoremove in singlebmpstoremove:
            bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
            bmptypename = self.jeeves.bmp.single_bmptype_from_bmpid(bmpid=bmpid)
            mask = pd.Series(newtable['bmpid'] == bmpid)
            newtable = newtable[~mask]
            removaltotal += mask.sum()
            logger.debug('removing %d for %s (type=%s)' % (mask.sum(), bmpnametoremove, bmptypename))

        # Remove "AllLoadSources" loadsourcegroup from the manure table
        loadsourcenametoremove = 'AllLoadSources'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        logger.debug('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove "FEEDPermitted" and "FEEDNonPermitted" loadsourcegroups from the manure table,
        # leaving only "FEED", which contains both anyway
        loadsourcenametoremove = 'FEEDPermitted'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        logger.debug('removing %d for %s' % (mask.sum(), loadsourcenametoremove))
        loadsourcenametoremove = 'FEEDNonPermitted'
        loadsourcegroupid = self.jeeves.loadsource. \
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        logger.debug('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Add together the AnimalUnits and AnimalCount for Permitted and NonPermitted
        keycols = ['loadsourcegroupid', 'bmpid', 'baseconditionid', 'countyidFrom', 'countyidTo', 'animalid', 'agencyid']
        # use fillna(-1) because out-of-the-watershed manure transport is represented by countyidTo==np.nan
        newtable = newtable.fillna(-1).groupby(keycols)['animalcount', 'animalunits'].sum().reset_index()
        # replace all of the -1 's in countyidTo column with np.nan again (by reassigning the previous values >=0)
        newtable = newtable.assign(countyidTo=newtable.countyidTo.where(newtable.countyidTo.ge(0)))
        # Remove any duplicate rows. (these are created when loadsourceids are matched to loadsourcegroupids
        newtable.drop_duplicates()

        self.idtable = newtable
        newrowcnt, newcolcnt = self.idtable.shape
        logger.debug('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                     (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_units_and_bounds(self):
        self.idtable = self.jeeves.bmp.append_unitids_to_table_with_bmpids(bmpidtable=self.idtable)
        # Manure can't be submitted as percent, but rather must be in Dry Tons.
        # So, let's calculate the maximum Dry Tons per animal, per county for this basecondition
        self.idtable['lowerbound'] = 0

        tempforcalc = self.idtable.copy()
        tempforcalc.rename(columns={'countyidFrom': 'countyid'}, inplace=True)
        tempforcalc = self.jeeves.animal.manuredrytons_from(basecondcountyanimalids=tempforcalc)
        self.idtable['upperbound'] = tempforcalc.manurelbsperanimalunitdaily * tempforcalc.animalunits
        self.idtable.rename(columns={'countyid': 'countyidFrom'}, inplace=True)

        return self.idtable.copy()


