
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
get_ipython().run_line_magic('pylab', 'inline')
from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from src.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars

# from src.subproblem_model_costobjective_county import CostObj


# ## Create problem instance

# In[2]:


# Load data for each set, parameter, etc. to define a problem instance
objwrapper = CostObj()
# lrsegs = ['N42071SL2_2410_2700']
# lrsegs = ['N51133RL0_6450_0000']
# lrsegs = ['N51133PL0_6270_0000']
lrsegs = ['N51133PL0_6140_0000']
data = objwrapper.load_data(savedata2file=False, lrsegs_list=lrsegs)
# data = objwrapper.load_data(savedata2file=False, county_list=['Northumberland, VA'])

# ---- Set the tau target load ----
for k in data.tau:
    data.tau[k] = 12
    taustr = str(round(data.tau[k], 1))
    
# Create concrete problem instance using the separately defined optimization model
mdl = objwrapper.create_concrete(data=data)
# Print the target load reduction values
for l in mdl.LRSEGS:
    print('%s: %d' % (mdl.tau[l,'N'], mdl.tau[l,'N'].value))
    mdl.TargetPercentReduction[l,'P'].deactivate()
    mdl.TargetPercentReduction[l,'S'].deactivate()
#     for p in mdl.PLTNTS:
#         print('%s: %d' % (mdl.tau[l,p], mdl.tau[l,p].value))

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# ## Solve problem instance

# In[3]:


from collections import OrderedDict

df_list = []
solution_objectives = OrderedDict()
for ii in range(1, 10):
    print(ii)
    
    # Reassign the target load values (tau)
    newtau = ii
    for k in data.tau:
        mdl.tau[k] = newtau
        print(mdl.tau[k].value)
        taustr = str(round(mdl.tau[k].value, 1))
        
    # Set names for saving output
    looptimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    loopname = ''.join(['output/costobj_tau', taustr, '_', solvername, '_',
                           looptimestamp])
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    IpoptParser().modify_ipopt_options(optionsfilepath='ipopt.opt', newfileprintlevel='2')
    merged_df = myobj.solve()
    print('\nObjective is: %d' % oe.value(mdl.Total_Cost))
    
    # Save this run's objective value in a list
    solution_objectives[mdl.tau[k].value] = oe.value(mdl.Total_Cost)
    merged_df['solution_objectives'] = oe.value(mdl.Total_Cost)
    
    # Label this run in the dataframe
    merged_df['tau'] = mdl.tau[k].value
    sorteddf_byacres = merged_df.sort_values(by='acres')
    
    
#     # ---- Make zL Figure ----
#     savefilepathandname = os.path.join(projectpath, ''.join([loopname, '_zL', .png']))

#     zL_bars(df=merged_df, instance=mdl,
#             savefig=True, savefilepathandname=savefilepathandname)
    
    
#     # ---- Make Acres Figure ----
#     savefilepathandname = os.path.join(projectpath, ''.join([loopname, '_x', .png']))

#     objstr = ''.join(['Objective is: ', str(round(mdl.Total_Cost(), 2))])
#     titlestr = '\n'.join([objstr, 'labels are (cost per unit, total bmp instance cost)'])

#     acres_bars(df=sorteddf_byacres, instance=mdl, titlestr=titlestr,
#                savefig=True, savefilepathandname=savefilepathandname)
    
#     # -- Gradient, Jacobian, Hessian
#     gjh_filename, g = gjh_solve(instance=mdl,
#                             keepfiles=True,
#                             amplenv=ampl,
#                             basegjhpath=os.getcwd())

#     g_df = make_df(instance=mdl, filterbydf=merged_df, g=g)

#     g_df = sorteddf_byacres.merge(g_df, how='left',
#                                   on=['bmpshortname', 'landriversegment', 'loadsource'],
#                                   sort=False)
    
#     # ---- Make gradient Figure ----
#     g_df_filtered = g_df
#     keystrs = [str([x, y]) for x, y in zip(g_df_filtered['bmpshortname'], g_df_filtered['loadsource'])]
#     # Make Figure
#     fig = plt.figure(figsize=(10, 4))
#     rects = plt.barh(y=keystrs, width=g_df_filtered['g'])
#     ax = plt.gca()

#     ax.set_position([0.3,0.1,0.5,0.8])
#     plt.savefig(os.path.join(projectpath, ''.join([loopname, '_g', .png']))))
    
    # Save all of the solutions in a list
    df_list.append(sorteddf_byacres)
    
# Save the results to a .csv file
alldfs = pd.concat(df_list, ignore_index=True)
alldfs['x'] = list(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
filenamestr = ''.join(['output/costobj_tausequence_alldfs', '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.csv'])
alldfs.to_csv(os.path.join(projectpath, filenamestr))


# In[4]:


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
