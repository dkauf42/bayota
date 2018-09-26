
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
get_ipython().run_line_magic('pylab', 'inline')
from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from src.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars


# ## Create problem instance

# In[2]:


# Load data for each set, parameter, etc. to define a problem instance
objwrapper = LoadObj()
# lrsegs = ['N42071SL2_2410_2700']
lrsegs = ['N51133RL0_6450_0000']
data = objwrapper.load_data(savedata2file=False, lrsegs_list=lrsegs)

# Set the cost bound ----
data.totalcostupperbound = 100000
costboundstr = str(round(data.totalcostupperbound, 1))

# Create concrete problem instance using the separately defined optimization model
mdl = objwrapper.create_concrete(data=data)

# Retain only the Nitrogen load objective, and deactivate the others
mdl.PercentReduction['P'].deactivate()
mdl.PercentReduction['S'].deactivate()

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# ## Solve problem instance

# In[3]:


df_list = []
solution_objectives = OrderedDict()
for ii in range(10):
    print(ii)
    
    # reinitialize the variables
    for k in mdl.x:
#         mdl.x[k] = float(random.randrange(0, 600001))/100
        mdl.x[k] = round(random.uniform(0, 6000), 2)
    
    # print the cost bound values (C)
    costboundstr = str(round(data.totalcostupperbound, 1))
    print(costboundstr)
    
    # Set names for saving output
    looptimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    loopname = ''.join(['output/loadobj_startingpoint', str(ii),
                        '_costbound', costboundstr, '_', solvername, '_',
                           looptimestamp])
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    logfilename = os.path.join(projectpath, ''.join([loopname, '.txt']))
    # set filepath for saving information about all of the solver iterates
    myobj.modify_ipopt_options(optionsfilepath='ipopt.opt',
                               newoutputfilepath=os.path.join(projectpath, ''.join([loopname, '.iters'])))
    merged_df = myobj.solve(logfilename=logfilename)
    print('shape of df is: %s' % str(merged_df.shape))
    print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))
    
    # Save this run's objective value in a list
    solution_objectives[mdl.totalcostupperbound.value] = oe.value(mdl.PercentReduction['N'])
    merged_df['solution_objectives'] = oe.value(mdl.PercentReduction['N'])
    
    # Label this run in the dataframe
    merged_df['totalcostupperbound'] = mdl.totalcostupperbound.value
    merged_df['startpointiterate'] = ii
    sorteddf_byacres = merged_df.sort_values(by='acres')
    
#     # ---- Make zL Figure ----
#     savefilepathandname = os.path.join(PROJECT_DIR, ''.join([loopname, '_zL', .png']))

#     zL_bars(df=merged_df, instance=mdl,
#             savefig=True, savefilepathandname=savefilepathandname)
    
#     # ---- Acres Figure ----
#     savefilepathandname = os.path.join(PROJECT_DIR, ''.join([loopname, '_x', .png']))

#     objstr = ''.join(['Objective is: ', str(round(oe.value(mdl.PercentReduction['N']),2))])
#     coststr = ''.join(['Total cost is: ', str(round(oe.value(mdl.Total_Cost.body),1))])
#     titlestr = '\n'.join([objstr, coststr, 'labels are (cost per unit, total bmp instance cost)'])

#     acres_bars(df=sorteddf_byacres, instance=mdl, titlestr=titlestr,
#                savefig=True, savefilepathandname=savefilepathandname)    
    
#     # -- Gradient, Jacobian, Hessian
#     gjh_filename, g = gjh_solve(instance=mdl,
#                             keepfiles=True,
#                             amplenv=ampl,
#                             basegjhpath=os.getcwd())

#     g_df = make_df(instance=mdl, filterbydf=merged_df, g=g)

#     sorteddf_byacres = sorteddf_byacres.merge(g_df, how='left',
#                                   on=['bmpshortname', 'landriversegment', 'loadsource'],
#                                   sort=False)
    
#     # ---- Make gradient Figure ----
#     keystrs = [str([x, y]) for x, y in zip(sorteddf_byacres['bmpshortname'], sorteddf_byacres['loadsource'])]
#     # Make Figure
#     fig = plt.figure(figsize=(10, 4))
#     rects = plt.barh(y=keystrs, width=sorteddf_byacres['g'])
#     ax = plt.gca()

#     ax.set_position([0.3,0.1,0.5,0.8])

#     plt.savefig(os.path.join(PROJECT_DIR, ''.join([loopname, '_g', .png'])))
    
    
    
# Save all of the solutions in a list
df_list.append(sorteddf_byacres)

# Save the results to a .csv file
alldfs = pd.concat(df_list, ignore_index=True)
alldfs['x'] = list(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
filenamestr = ''.join(['output/loadobj_difstartpts_alldfs', '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.csv'])
alldfs.to_csv(os.path.join(projectpath, filenamestr))


# In[4]:


# solver = oe.SolverFactory('ipopt')
# results = solver.solve(mdl, tee=True, symbolic_solver_labels=True,
#                                    keepfiles=False)


# In[5]:


i=0
for v in mdl.component_data_objects(oe.Var):
    if v.stale:
        continue
    i+=1
#     print(str(v), ' = ', value(v))
    
print(i)


# In[6]:


# for k in mdl.x.keys():
#     print(mdl.x[k].stale)


# In[7]:


from src.solution_handlers.solution_wrangler import get_nonzero_var_names_and_values
nzvnames, nzvvalues = get_nonzero_var_names_and_values(mdl, onlynotstale=True)


# In[8]:


print(len(nzvnames))
nzvnames[1]


# In[9]:


from src.solution_handlers.solution_wrangler import get_nonzero_var_df
nonzerodf = get_nonzero_var_df(mdl, addcosttbldata=data.costsubtbl)


# In[10]:


print(nonzerodf.shape)
nonzerodf.head(5)


# In[11]:


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

