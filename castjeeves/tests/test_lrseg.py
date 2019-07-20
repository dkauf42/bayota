import pytest
import pandas as pd

from castjeeves.jeeves import Jeeves
from castjeeves.sourcehooks import Lrseg


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Lrseg(sourcedata=source)

def test_lrseg_all_names_query_as_list(resource_a):
    retval = resource_a.all_names(astype=list)
    assert ('N24003WL0_4601_0000' in retval) and isinstance(retval, list)

def test_lrseg_all_names_query_as_Series(resource_a):
    retval = resource_a.all_names(astype='series')
    assert ('N24003WL0_4601_0000' in retval.tolist()) and isinstance(retval, pd.Series)

def test_removal_of_outofcbws_lrsegs_from_list(resource_a):
    lrseglist = ['N36007ZZ0_9999_9999',
                 'N36007SU5_0420_0500',
                 'N36007SU4_0430_0420',
                 'N36007SU2_0440_0550']
    autoremoved = resource_a.remove_outofcbws_lrsegs(lrseglist=lrseglist)
    lrseglist.remove('N36007ZZ0_9999_9999')

    assert set(autoremoved) == set(lrseglist)

def test_removal_of_outofcbws_lrsegs_from_dataframe(resource_a):
    lrsegdf = pd.DataFrame(data=['N36007ZZ0_9999_9999',
                                 'N36007SU5_0420_0500',
                                 'N36007SU4_0430_0420',
                                 'N36007SU2_0440_0550'],
                           columns=['landriversegment'])
    autoremoved = resource_a.remove_outofcbws_lrsegs(lrsegdf=lrsegdf)['landriversegment']
    lrseglist = lrsegdf['landriversegment'].tolist()
    lrseglist.remove('N36007ZZ0_9999_9999')

    assert set(autoremoved) == set(lrseglist)
