import os
from amplpy import AMPL, Environment

# %pylab inline

baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'OptEfficiencySubProblem/')
amplappdir = os.path.join(baseexppath, 'ampl/amplide.macosx64/')

ampl = AMPL(Environment(amplappdir))
