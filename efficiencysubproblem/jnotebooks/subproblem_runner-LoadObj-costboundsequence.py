
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
lrsegs = ['N42071SL2_2410_2700']
# lrsegs = ['N51133RL0_6450_0000']
data = objwrapper.load_data(savedata2file=False, lrsegs_list=lrsegs)

# Set the cost bound ----
data.totalcostupperbound = 0
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
    
    # Reassign the cost bound values (C)
    data.totalcostupperbound = data.totalcostupperbound + 100000
    mdl.totalcostupperbound = data.totalcostupperbound
    costboundstr = str(round(data.totalcostupperbound, 1))
    print(costboundstr)
    
    # Set names for saving output
    looptimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    loopname = ''.join(['output/loadobj_costbound', costboundstr, '_', solvername, '_',
                           looptimestamp])
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    merged_df = myobj.solve()
    print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))
    
    # Save this run's objective value in a list
    solution_objectives[mdl.totalcostupperbound.value] = oe.value(mdl.PercentReduction['N'])
    merged_df['solution_objectives'] = oe.value(mdl.PercentReduction['N'])
    
    # Label this run in the dataframe
    merged_df['totalcostupperbound'] = mdl.totalcostupperbound.value
    sorteddf_byacres = merged_df.sort_values(by='acres')
    
    # -- Gradient, Jacobian, Hessian
    gjh_filename, g = gjh_solve(instance=mdl,
                            keepfiles=True,
                            amplenv=ampl,
                            basegjhpath=os.getcwd())

    g_df = make_df(instance=mdl, filterbydf=merged_df, g=g)

    sorteddf_byacres = sorteddf_byacres.merge(g_df, how='left',
                                  on=['bmpshortname', 'landriversegment', 'loadsource'],
                                  sort=False)
    
    sorteddf_byacres.iloc[sorteddf_byacres['g'].idxmin(), :]
    mingidx = sorteddf_byacres['g'].idxmin()
    
    # ----------- figure creations ------------ #
    ordered_var_names = ['g', 'acres', 'z_l']
    ordered_var_strs = ['gradient', 'values', 'z_L']
    # ordered_yranges = [[-20,0], [0,1000], [0,100000]]
    ordered_yranges = [None, None, None]
    ordered_xranges = [None, None, None]

    # We can ask for ALL THE AXES and put them into axes
    fig, axes = plt.subplots(nrows=1,
                             ncols=len(ordered_var_names),
                             sharex=False, sharey=True, figsize=(10, 12))
    # axes_list = [item for sublist in axes for item in sublist]
    axes_list = [item for item in axes]

    for count, v in enumerate(ordered_var_names):
        ax = axes[count]
        keystrs = [str([x, y])
                   for x, y in zip(sorteddf_byacres['bmpshortname'],
                                   sorteddf_byacres['loadsource'])]
        
        if v=='z_l':
            rects = ax.barh(y=keystrs, width=sorteddf_byacres['zL'])
        elif v=='g':
            rects = ax.barh(y=keystrs, width=sorteddf_byacres['g'])
        elif v=='acres':
            coststrs = ['(%.1f, %.1f)' %
                        (round(x, 1), round(y, 1))
                        if (y > 1e-6) else ''
                        for x, y in zip(list(sorteddf_byacres['totalannualizedcostperunit']),
                                        list(sorteddf_byacres['totalinstancecost']))]
            
            rects = ax.barh(y=keystrs, width=sorteddf_byacres['acres'])
            for rect, label in zip(rects, coststrs):
                width = rect.get_width()
                ax.text(width + 0.1, rect.get_y() + rect.get_height() / 2,
                         label,
                         ha='left', va='center')
            rects[mingidx].set_color((0.8627, 0.3569, 0.1569))

#             plt.title(titlestr)
            
#         ax.set_position([0.3,0.1,0.5,0.8])
        
        ax.set_ylabel(v, rotation=0, horizontalalignment='right')
        ax.set_title(ordered_var_strs[count])
        ax.tick_params(
            which='both',
            bottom=False,
            left=False,
            right=False,
            top=False
        )
        ax.grid(linewidth=0.25)
    #     ax.set_xlim((first_x, last_x))
    #     ax.set_xticks((first_x, last_x))
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        axes_list.remove(ax)

    # Now use the matplotlib .remove() method to 
    # delete anything we didn't use
    for ax in axes_list:
        ax.remove()

    # fig.text(0.5, 0.00, 'Total Cost Upper Bound', ha='center')

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.2)

    savefilepathandname = os.path.join(projectpath, ''.join([loopname, '_gxz', '.png']))
    plt.savefig(savefilepathandname)
    
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
    
asdkjhagsd
# Save the results to a .csv file
alldfs = pd.concat(df_list, ignore_index=True)
alldfs['x'] = list(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
filenamestr = ''.join(['output/loadobj_costboundsequence_alldfs', '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.csv'])
alldfs.to_csv(os.path.join(projectpath, filenamestr))


# In[ ]:


for mdl.


# In[14]:


mdl.dual.pprint()


# In[6]:


# ----------- figure creations ------------ #
ordered_var_names = ['g', 'acres', 'z_l']
ordered_var_strs = ['gradient', 'values', 'z_L']
# ordered_yranges = [[-20,0], [0,1000], [0,100000]]
ordered_yranges = [None, None, None]
ordered_xranges = [None, None, None]

# We can ask for ALL THE AXES and put them into axes
fig, axes = plt.subplots(nrows=1,
                         ncols=len(ordered_var_names),
                         sharex=False, sharey=True, figsize=(10, 12))
# axes_list = [item for sublist in axes for item in sublist]
axes_list = [item for item in axes]

for count, v in enumerate(ordered_var_names):
    ax = axes[count]
    keystrs = [str([x, y])
               for x, y in zip(sorteddf_byacres['bmpshortname'],
                               sorteddf_byacres['loadsource'])]

    if v=='z_l':
        rects = ax.barh(y=keystrs, width=sorteddf_byacres['zL'])
    elif v=='g':
        rects = ax.barh(y=keystrs, width=sorteddf_byacres['g'])
    elif v=='acres':
        coststrs = ['(%.1f, %.1f)' %
                    (round(x, 1), round(y, 1))
                    if (y > 1e-6) else ''
                    for x, y in zip(list(sorteddf_byacres['totalannualizedcostperunit']),
                                    list(sorteddf_byacres['totalinstancecost']))]

        rects = ax.barh(y=keystrs, width=sorteddf_byacres['acres'])
        for rect, label in zip(rects, coststrs):
            width = rect.get_width()
            ax.text(width + 0.1, rect.get_y() + rect.get_height() / 2,
                     label,
                     ha='left', va='center')
        rects[mingidx].set_color((0.8627, 0.3569, 0.1569))

#             plt.title(titlestr)

#         ax.set_position([0.3,0.1,0.5,0.8])

    ax.set_ylabel(v, rotation=0, horizontalalignment='right')
    ax.set_title(ordered_var_strs[count])
    ax.tick_params(
        which='both',
        bottom=False,
        left=False,
        right=False,
        top=False
    )
    ax.grid(linewidth=0.25)
#     ax.set_xlim((first_x, last_x))
#     ax.set_xticks((first_x, last_x))
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    axes_list.remove(ax)

# Now use the matplotlib .remove() method to 
# delete anything we didn't use
for ax in axes_list:
    ax.remove()

# fig.text(0.5, 0.00, 'Total Cost Upper Bound', ha='center')

plt.tight_layout()
plt.subplots_adjust(hspace=0.2)


# In[7]:


# sorteddf_byacres.iloc[sorteddf_byacres['g'].idxmin(), :]
display(sorteddf_byacres.loc[:,['bmpshortname', 'loadsource','g']])


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

