
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from util.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars
get_ipython().run_line_magic('pylab', 'inline')


# ## Create problem instance

# In[3]:


# Load data for each set, parameter, etc. to define a problem instance
objwrapper = LoadObj()
data = objwrapper.load_data(savedata2file=False)

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

# In[4]:


from collections import OrderedDict

df_list = []
solution_objectives = OrderedDict()
for ii in range(1, 10):
    print(ii)
    
    # Reassign the cost bound values (C)
    data.totalcostupperbound = data.totalcostupperbound + 100000
    mdl.totalcostupperbound = data.totalcostupperbound
    costboundstr = str(round(data.totalcostupperbound, 1))
    print(costboundstr)
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    merged_df = myobj.solve()
    print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))
    
    # Label this run in the dataframe
    merged_df['totalcostupperbound'] = mdl.totalcostupperbound.value
    
    # Save this run's objective value in a list
    solution_objectives[mdl.totalcostupperbound.value] = oe.value(mdl.PercentReduction['N'])
    
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
    
    df_list.append(merged_df)
    


# In[5]:


alldfs = pd.concat(df_list)
print(type(alldfs))
print(alldfs.shape)

alldfs['x'] = list(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
display(alldfs.head(2))

df_piv = alldfs.pivot(index='totalcostupperbound', columns='x', values='acres')

df_piv.reset_index(level=['totalcostupperbound'], inplace=True)  # make totalcostupperbound into a regular column
display(df_piv.head(3))

df_piv['range']=df_piv.drop('totalcostupperbound', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
display(df_piv.tail(3))

# get unique BMP-LRseg-Loadsource combinations:
# ucombos = set(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource))

# solution_objectives
df_piv['objective'] = df_piv['totalcostupperbound'].map(solution_objectives)
df_piv.head(3)


# In[6]:


# plotly.plot(df_piv['totalcostupperbound'], df_piv['objective'])

# Create a trace
trace = go.Scatter(
    x = df_piv['totalcostupperbound'],
    y = df_piv['objective']
)

data = [trace]

# Edit the layout
layout = dict(title = 'Max Load Reduction vs. Total Cost Constraint',
              xaxis = dict(title = 'Total Cost ($) Upper Bound Constraint'),
              yaxis = dict(title = 'Maximal Load Reduction (%)'),
              paper_bgcolor='rgba(0,0,0,0)',
              plot_bgcolor='rgba(0,0,0,0)'
              )

fig = dict(data=data, layout=layout)
py.iplot(fig, filename='styled-line')


py.image.save_as(fig, filename='a-simple-plot_loadobj.png', scale=5)


# In[7]:


fig = plt.figure(figsize=(10, 12))
ax = sns.heatmap(df_piv[df_piv.columns.difference(['totalcostupperbound', 'range', 'objective'])].T,
                cmap='viridis',
                cbar_kws={'label': 'acres'},
                xticklabels=list( '%s\n(%.1f)' % ("${0:,.0f}".format(x),y)
                                 for x,y in
                                 zip(df_piv['totalcostupperbound'], round(df_piv['objective'],1))
                                )
                )
plt.xlabel("totalcostupperbound (max % load reduction achieved)")

filenamestr = ''.join(['output/loadobj_heatmap_costboundsequence_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname, bbox_inches='tight')


# In[8]:


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


# In[9]:


# from matplotlib import pyplot as plt
# # barh(range(len(res)),res.values(), align='center')
# fig = plt.figure(figsize=(10, 4))
# rects = plt.barh(y=nzvarnames, width=nzvarvalus)
# ax = plt.gca()
# # ax.tick_params(axis='x', colors='white')

