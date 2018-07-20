
# coding: utf-8

# In[10]:


import os
import pyomo.environ as oe
import pandas as pd
from pyomo.opt import SolverFactory
from subproblem_model import build_subproblem_model
from subproblem_dataloader import DataLoader


# In[12]:


baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')


# In[2]:


data = DataLoader()


# In[3]:


#display(data.BMPGRPING)
#display(data.BMPGRPING)


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
                             tau=data.tau,
                             phi=data.phi,
                             t=data.T)


# In[8]:


get_ipython().run_line_magic('pylab', 'inline')
from datetime import datetime


# In[13]:


for ii in range(1, 10):
    print(ii)
    
    # Reassign the target load values (tau)
    newtau = ii
    for k in data.tau:
        mdl.tau[k] = newtau
        print(mdl.tau[k].value)
        
    # Solve The Model
    solver = SolverFactory("minos")
    results = solver.solve(mdl, tee=True, symbolic_solver_labels=True)
    print('Objective is: %d' % mdl.Total_Cost())
    # print(results)
    
    # Extract just the nonzero optimal variable values
    tol = 1e-6
    nzvarnames = []
    nzvarvalus = []
    for k in mdl.x.keys():
        if (not not mdl.x[k].value):
            if abs(mdl.x[k].value)>tol:
                nzvarnames.append(mdl.x[k].getname())
                nzvarvalus.append(mdl.x[k].value)
    # Repeat the same thing, but make a DataFrame
    nonzerokeyvals_df = pd.DataFrame([[k, mdl.x[k].value]
                                      for k in mdl.x.keys()
                                      if (not not mdl.x[k].value) 
                                      if abs(mdl.x[k].value)>tol],
                                     columns=['key', 'value'])
    # display(nonzerokeyvals_df.head(2))
    nonzerodf = pd.DataFrame.from_dict([{'bmpshortname':x[0], 'landriversegment':x[1],
                                         'loadsource': x[2], 'acres': y}
                                        for x, y in zip(nonzerokeyvals_df.key, nonzerokeyvals_df.value)])
    # display(nonzerodf.head(2))
    
    # add cost/unit data to results table
    costsubtbl = data.costsubtbl
    # Retain only those costs pertaining to bmps in our set
    includecols = ['totalannualizedcostperunit', 'bmpshortname']
    nonzerodf = nonzerodf.merge(costsubtbl.loc[:,includecols])
    # display(nonzerodf.head(2))
    
    # Add total cost of each BMP to results table for this instance
    nonzerodf['totalinstancecost'] = np.multiply(nonzerodf['totalannualizedcostperunit'].values,
                                                 nonzerodf['acres'].values)
    # display(nonzerodf.head(2))
    coststrs = [str(x) for x in zip(list(nonzerodf['totalannualizedcostperunit']),
                                    list(nonzerodf['totalinstancecost']))]
    # display(coststrs)
    
    
    keystrs = [str([x, y]) for x, y in zip(nonzerodf['bmpshortname'], nonzerodf['loadsource'])]
    
    
    # Make Figure
    fig = plt.figure(figsize=(10, 4))
    rects = plt.barh(y=keystrs, width=nonzerodf['acres'])
    ax = plt.gca()
    
    for rect, label in zip(rects, coststrs):
        width = rect.get_width()
        plt.text(width + 0.1, rect.get_y() + rect.get_height() / 2, label,
                ha='left', va='center')
    
    objstr = ''.join(['Objective is: ', str(mdl.Total_Cost())])
    labelstr = 'labels are (cost per unit, total bmp instance cost)'
    plt.title('\n'.join([objstr, labelstr]))
    
    ax.set_position([0.3,0.1,0.5,0.8])
    #plt.tight_layout()
    
    filestr = ''.join(['output/tau%sN%sP%sS_minos_' % (newtau, newtau, newtau),
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'),'.png'])
    plt.savefig(os.path.join(projectpath, filestr))
    


# In[ ]:


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


# In[ ]:


# from matplotlib import pyplot as plt
# # barh(range(len(res)),res.values(), align='center')
# fig = plt.figure(figsize=(10, 4))
# rects = plt.barh(y=nzvarnames, width=nzvarvalus)
# ax = plt.gca()
# # ax.tick_params(axis='x', colors='white')

