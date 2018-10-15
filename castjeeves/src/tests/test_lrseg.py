import pytest
import pandas as pd

from ..jeeves import Jeeves
from ..sourcehooks.lrseg import Lrseg


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Lrseg(sourcedata=source)


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