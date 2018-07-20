
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories

import os
import pyomo.environ as oe
import pandas as pd
from pyomo.opt import SolverFactory, SolverManagerFactory
from amplpy import AMPL, Environment

from util.subproblem_model_loadobjective import build_subproblem_model
from util.subproblem_dataloader import DataLoader
from util.subproblem_solver_ipopt import SolveAndParse
from util.gjh_wrapper import gjh_solve, make_df
from vis.acres_bars import acres_bars
from vis.zL_bars import zL_bars

get_ipython().run_line_magic('pylab', 'inline')
from datetime import datetime


# In[2]:


baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')
amplappdir = os.path.join(baseexppath, 'ampl/amplide.macosx64/')
ampl = AMPL(Environment(amplappdir))


# In[3]:


from sys import path as pylib #im naming it as pylib so that we won't get confused between os.path and sys.path 

# pylib += [os.path.abspath(os.path.join(ROOT_DIR, '../castjeeves'))]

pylib.append(os.path.abspath('/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/CastJeeves'))
# print(pylib)
from CastJeeves.jeeves import Jeeves


# In[4]:


cj = Jeeves()
# print(cj.geo.all_geotypes())


# ## Load data for each set, parameter, etc. to define a problem instance

# In[5]:


data = DataLoader(save2file=False)

# ---- Cost bound ----
data.totalcostupperbound = 2827702
costboundstr = str(round(data.totalcostupperbound, 1))

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# In[6]:


data.phi


# ### Create concrete problem instance using the separately defined optimization model

# In[7]:


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


# In[8]:


# Retain only the Nitrogen load objective, and deactivate the others
mdl.PercentReduction['P'].deactivate()
mdl.PercentReduction['S'].deactivate()


# ## Solve problem instance

# In[9]:


myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
merged_df = myobj.solve()
print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))


# In[10]:


temp_df = pd.DataFrame([[k.index(), mdl.dual[k]]
                            for k in mdl.dual.keys()],
                           columns=['key', 'value'])
# temp_df.dropna(inplace=True)
display(temp_df.tail(5))
print(temp_df.shape[0])

[mdl.BMPS[temp_df.key[x][0]] for x in range(1,temp_df.shape[0])]
# mdl.BMPS[temp_df.key[x][0] for x in temp_df.shape[0]]


# In[11]:


# from util.solution_wrangler import get_dual_df
# dual_df = get_dual_df(mdl)
# display(dual_df.tail(5))


# In[12]:


# display(dual_df.loc[dual_df.bmpshortname == 'HRTill'])
# display(dual_df.tail(20))


# In[13]:


# tempdf_withduals = merged_df.merge(dual_df, how='left',
#                                    on=['bmpshortname', 'landriversegment', 'loadsource'])
# display(tempdf_withduals.head(30))


# ## Visualize

# In[14]:


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


# In[15]:


# ---- Acres Figure ----
sorteddf_byacres = merged_df.sort_values(by='acres')

filenamestr = ''.join(['output/loadobj_x_costbound', costboundstr, '_', solvername, '_',
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

objstr = ''.join(['Objective is: ', str(round(oe.value(mdl.PercentReduction['N']),2))])
coststr = ''.join(['Total cost is: ', str(round(oe.value(mdl.Total_Cost.body),1))])
titlestr = '\n'.join([objstr, coststr, 'labels are (cost per unit, total bmp instance cost)'])

acres_bars(df=sorteddf_byacres, instance=mdl, titlestr=titlestr,
           savefig=True, savefilepathandname=savefilepathandname)


# ## Gradient, Jacobian, Hessian

# In[16]:


gjh_filename, g = gjh_solve(instance=mdl,
                            keepfiles=True,
                            amplenv=ampl,
                            basegjhpath=os.getcwd())

g_df = make_df(instance=mdl, filterbydf=merged_df, g=g)

g_df = sorteddf_byacres.merge(g_df, how='left',
                              on=['bmpshortname', 'landriversegment', 'loadsource'],
                              sort=False)


# In[17]:


# ---- Make gradient Figure ----
# g_df_filtered = g_df.loc[abs(g_df['g'])>0.001,:].copy()
g_df_filtered = g_df
# sorteddf = g_df_filtered.sort_values(by='g')
# sorteddf_byacres

# sorteddf_byacres
# g_df = g_df.merge(sorteddf_byacres, how='right',
#                on=['bmpshortname', 'landriversegment', 'loadsource'])

keystrs = [str([x, y]) for x, y in zip(g_df_filtered['bmpshortname'], g_df_filtered['loadsource'])]
# Make Figure
fig = plt.figure(figsize=(10, 4))
rects = plt.barh(y=keystrs, width=g_df_filtered['g'])
ax = plt.gca()

ax.set_position([0.3,0.1,0.5,0.8])


filenamestr = ''.join(['output/loadobj_g_costbound', costboundstr, '_', solvername, '_',
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                       '.png'])
plt.savefig(os.path.join(projectpath, filenamestr))


# ## Use the IPOPT derivative test

# In[18]:


solver = SolverFactory(solvername)

# Using the 'ipopt.opt' options file if in this same directory

mdl.jac_g = oe.Suffix(direction=oe.Suffix.IMPORT)
mdl.grad_f = oe.Suffix(direction=oe.Suffix.IMPORT)

results = solver.solve(mdl, tee=True, symbolic_solver_labels=True, keepfiles=True,
                       logfile='logfile_loadobjective_derivativetest.log')


# In[19]:


mdl.grad_f.pprint()


# In[20]:


mdl.x.pprint()

