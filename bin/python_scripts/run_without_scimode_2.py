import pandas as pd

from castjeeves.jeeves import Jeeves


jeeves = Jeeves()

pd.set_option('display.float_format', lambda x: '{:,.1f}'.format(x))

def numstr(number, decimalpoints: int) -> str:
    """ Add commas, and restrict decimal places """
    fmtstr = '{:,.%sf}' % str(decimalpoints)
    return fmtstr.format(number)


model_spec_file = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/specification_files/model_specs/costmin_total_Npercentreduction.yaml'
# model_spec_file = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/bayota/bin/specification_files/model_specs/Nloadreductionmax_totalcostupper.yaml'
# mdlhandler = model_generator.ModelBuilder(model_spec_file=model_spec_file,
#                                               geoscale='county',
#                                               geoentities='Perry, PA',
#                                               savedata2file=False,
#                                               baseloadingfilename='2010NoActionLoads.csv')
# mdl = mdlhandler.model

from bayom_e.data_handling.data_interface import DataHandlerCounty

dh = DataHandlerCounty(geolist=['Adams, PA'], baseloadingfilename='2010NoActionLoads_20190325.csv')

# import math
# for p in mdl.PLTNTS:
#     if math.isinf(pyo.value(mdl.original_load_expr[p])):
#         print(f"Uh oh! original_load_expr for {p} is Inf")
#     elif math.isnan(pyo.value(mdl.original_load_expr[p])):
#         print(f"Uh oh! original_load_expr for {p} is NaN")
#     else:
#         print("original_load_expr for %s is %s" % (p, numstr(pyo.value(mdl.original_load_expr[p]), 2)))