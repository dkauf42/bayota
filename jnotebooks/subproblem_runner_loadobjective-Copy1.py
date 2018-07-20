
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
data.totalcostupperbound = 359202.8992381379
costboundstr = str(round(data.totalcostupperbound, 1))

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# ### Create concrete problem instance using the separately defined optimization model

# In[6]:


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


# In[7]:


# Retain only the Nitrogen load objective, and deactivate the others
mdl.PercentReduction['P'].deactivate()
mdl.PercentReduction['S'].deactivate()


# ## Solve problem instance

# In[8]:


myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
merged_df = myobj.solve()
print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))


# ## Visualize

# In[9]:


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


# In[10]:


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


# In[11]:


asdasdkjhg


# ## Gradient, Jacobian, Hessian

# In[12]:


opt2 = SolverFactory('gjh')
r2 = opt2.solve(mdl, keepfiles=True)

# Get the output file name
import re
def all_same(items):
    return all([x == items[0] for x in items])
str1 = r2.Solver._list[0].Message
matches = re.findall('\w+\.pyomo\.gjh', str1)
print(all_same(matches))
gjh_filename = matches[0]
print(gjh_filename)


# In[13]:


r2dat = ampl.read(os.path.join(projectpath, gjh_filename))
g = ampl.getParameter('g')
g_df = g.getValues().toPandas()
display(g.getValues().toPandas().head(5))
g[1]


# In[24]:


dict_for_df = {}
for v in mdl.component_objects(oe.Var, active=True):
    print ("Variable component object",v)
    i=0
    for index in v:
        try:
            x_value = oe.value(v[index])
            i+=1
            try:
#                 print (i,"   ", index, v[index].value, g[i])
                
                dict_for_df[index] = g[i]     # store in a dict
                
            except:
                pass
#                 print (i,"   ", index, v[index].value)
        except:
            pass
        

g_df = pd.DataFrame.from_dict([{'bmpshortname': x[0],
                                'landriversegment': x[1],
                                'loadsource': x[2],
                                'g': y}
                               for x, y in zip(dict_for_df.keys(), dict_for_df.values())])
print(g_df.shape)
display(g_df.head(5))
#         i+=1
#         if not not v[index].value:
#             print (i,"   ", index, v[index].value)


# In[32]:


# ---- Make gradient Figure ----
g_df_filtered = g_df.loc[abs(g_df['g'])>0.001,:].copy()
sorteddf = g_df_filtered.sort_values(by='g')

keystrs = [str([x, y]) for x, y in zip(sorteddf['bmpshortname'], sorteddf['loadsource'])]
# Make Figure
fig = plt.figure(figsize=(10, 4))
rects = plt.barh(y=keystrs, width=sorteddf['g'])
ax = plt.gca()

ax.set_position([0.3,0.1,0.5,0.8])


# filenamestr = ''.join(['output/loadobj_zL_costbound', costboundstr, '_', solvername, '_',
#                        datetime.now().strftime('%Y-%m-%d_%H%M%S'),
#                        '.png'])
# plt.savefig(os.path.join(projectpath, filenamestr))


# In[ ]:


i=0
for xi in mdl.x.keys():
    try:
        x_value = oe.value(mdl.x[xi])
        i+=1
        
        print (i,"   ", xi, x_value, g[i])
    except:
        pass

