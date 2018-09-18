import os
from definitions import ROOT_DIR
from amplpy import AMPL, Environment

# %pylab inline

# baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'

projectpath = os.path.join(ROOT_DIR, 'efficiencysubproblem/')
amplappdir = os.path.join(ROOT_DIR, 'ampl/amplide.macosx64/')

# ampl = AMPL(Environment(amplappdir))
