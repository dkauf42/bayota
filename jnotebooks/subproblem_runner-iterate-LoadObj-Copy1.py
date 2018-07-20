
# coding: utf-8

# In[1]:


import os
import pyomo.environ as oe
import pandas as pd
from pyomo.opt import SolverFactory, SolverManagerFactory
from util.subproblem_model_loadobjective import build_subproblem_model
from util.subproblem_dataloader import DataLoader
from util.subproblem_solver_ipopt import SolveAndParse

from amplpy import AMPL, Environment
get_ipython().run_line_magic('pylab', 'inline')
from datetime import datetime


# In[2]:


baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')


# ## Load data for each set, parameter, etc. to define a problem instance

# In[3]:


data = DataLoader(save2file=False)

# ---- Cost bound ----
data.totalcostupperbound = 159202.8992381379
costboundstr = str(round(data.totalcostupperbound, 1))

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# ### Create concrete problem instance using the separately defined optimization model

# In[4]:


# Note that there is no need to call create_instance on a ConcreteModel
mdl = build_subproblem_model(pltnts=data.PLTNTS,
                             lrsegs=data.LRSEGS,
                             bmps=data.BMPS,
                             bmpgrps=data.BMPGRPS,
                             bmpgrping=data.BMPGRPING,
                             loadsrcs=data.LOADSRCS,
                             bmpsrclinks=data.BMPSRCLINKS,
                             bmpgrpsrclinks=data.BMPGRPSRCLINKS,
                             c=data.c,
                             e=data.E,
                             phi=data.phi,
                             t=data.T,
                             totalcostupperbound=data.totalcostupperbound)


# In[5]:


# Retain only the Nitrogen load objective, and deactivate the others
mdl.PercentReduction['P'].deactivate()
mdl.PercentReduction['S'].deactivate()


# ## Solve problem instance

# In[6]:


for ii in range(1, 10):
    print(ii)
    
    # Reassign the target load values (tau)
    data.totalcostupperbound = data.totalcostupperbound + 100000
    mdl.totalcostupperbound = data.totalcostupperbound
    costboundstr = str(round(data.totalcostupperbound, 1))
    print(costboundstr)
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    merged_df = myobj.solve()
    print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))
    
    
    # ---- Make zL Figure ----
    # zL_df_filtered = merged_df.loc[abs(merged_df['zL'])>0.45,:].copy()
    keystrs = [str([x, y]) for x, y in zip(merged_df['bmpshortname'], merged_df['loadsource'])]
    # Make Figure
    fig = plt.figure(figsize=(10, 4))
    rects = plt.barh(y=keystrs, width=merged_df['zL'])
    ax = plt.gca()

    ax.set_position([0.3,0.1,0.5,0.8])


    filenamestr = ''.join(['output/loadobj_zL_costbound', costboundstr, '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                           '.png'])
    plt.savefig(os.path.join(projectpath, filenamestr))
    
    
    
    # ---- Make acres Figure ----
    sorteddf = merged_df.sort_values(by='acres')
    coststrs = ['(%.1f, %.1f)' % (round(x,1), round(y,1)) for x, y in zip(list(sorteddf['totalannualizedcostperunit']),
                                                                          list(sorteddf['totalinstancecost']))]
    keystrs = [str([x, y]) for x, y in zip(sorteddf['bmpshortname'], sorteddf['loadsource'])]
    # Make Figure
    fig = plt.figure(figsize=(10, 4))
    rects = plt.barh(y=keystrs, width=sorteddf['acres'])
    ax = plt.gca()

    for rect, label in zip(rects, coststrs):
        width = rect.get_width()
        plt.text(width + 0.1, rect.get_y() + rect.get_height() / 2, label,
                ha='left', va='center')

    objstr = ''.join(['Objective is: ', str(round(oe.value(mdl.PercentReduction['N']),1))])
    coststr = ''.join(['Total cost is: ', str(round(oe.value(mdl.Total_Cost.body),1))])
    labelstr = 'labels are (cost per unit, total bmp instance cost)'
    plt.title('\n'.join([objstr, coststr, labelstr]))

    ax.set_position([0.3,0.1,0.5,0.8])

    filenamestr = ''.join(['output/loadobj_x_costbound', costboundstr, '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                           '.png'])
    plt.savefig(os.path.join(projectpath, filenamestr))
    


# In[7]:


# # Other ways to access the optimal values:
# mdl.x['HRTill', 'N51133RL0_6450_0000', 'oac'].value
#
# tol = 1e-6
# for b in mdl.BMPS:
#     for lmbda in mdl.LOADSRCS:
#         bval = mdl.x[b, 'N51133RL0_6450_0000', lmbda].value
#         if not not bval:
#             if abs(bval)>tol:
#                 print('(%s, %s): %d' % (b, lmbda, bval))


# In[8]:


# from matplotlib import pyplot as plt
# # barh(range(len(res)),res.values(), align='center')
# fig = plt.figure(figsize=(10, 4))
# rects = plt.barh(y=nzvarnames, width=nzvarvalus)
# ax = plt.gca()
# # ax.tick_params(axis='x', colors='white')

