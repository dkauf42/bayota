
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
objwrapper = CostObj()
data = objwrapper.load_data(savedata2file=False)

# ---- Set the tau target load ----
for k in data.tau:
    data.tau[k] = 12
    taustr = str(round(data.tau[k], 1))
# Print the target load reduction values
for l in mdl.LRSEGS:
    for p in mdl.PLTNTS:
        print('%s: %d' % (mdl.tau[l,p], mdl.tau[l,p].value))
    
# Create concrete problem instance using the separately defined optimization model
mdl = objwrapper.create_concrete(data=data)

# ---- Solver name ----
localsolver = True
solvername = 'ipopt'
# solvername = 'minos'


# ## Solve problem instance

# In[7]:


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
        
    # Solve The Model
    myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
    merged_df = myobj.solve()
    print('\nObjective is: %d' % oe.value(mdl.Total_Cost))
    
    # Label this run in the dataframe
    merged_df['tau'] = mdl.tau[k].value
    
    # Save this run's objective value in a list
    solution_objectives[mdl.tau[k].value] = oe.value(mdl.Total_Cost)
    
    
    # ---- Make zL Figure ----
    filenamestr = ''.join(['output/costobj_zL_tau', taustr, '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                           '.png'])
    savefilepathandname = os.path.join(projectpath, filenamestr)

    zL_bars(df=merged_df, instance=mdl,
            savefig=True, savefilepathandname=savefilepathandname)
    
    
    # ---- Make Acres Figure ----
    sorteddf_byacres = merged_df.sort_values(by='acres')

    filenamestr = ''.join(['output/costobj_x_tau', taustr, '_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
    savefilepathandname = os.path.join(projectpath, filenamestr)

    objstr = ''.join(['Objective is: ', str(round(mdl.Total_Cost(), 2))])
    titlestr = '\n'.join([objstr, 'labels are (cost per unit, total bmp instance cost)'])

    acres_bars(df=sorteddf_byacres, instance=mdl, titlestr=titlestr,
               savefig=True, savefilepathandname=savefilepathandname)
    
    df_list.append(merged_df)


# In[8]:


alldfs = pd.concat(df_list)
print(type(alldfs))
print(alldfs.shape)

alldfs['x'] = list(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource, alldfs.totalannualizedcostperunit))
display(alldfs.head(2))

df_piv = alldfs.pivot(index='tau', columns='x', values='acres')

df_piv.reset_index(level=['tau'], inplace=True)  # make tau into a regular column
display(df_piv.head(3))

df_piv['range']=df_piv.drop('tau', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
display(df_piv.tail(3))

# get unique BMP-LRseg-Loadsource combinations:
# ucombos = set(zip(alldfs.bmpshortname, alldfs.landriversegment, alldfs.loadsource))

# solution_objectives
df_piv['objective'] = df_piv['tau'].map(solution_objectives)
df_piv.head(3)


# In[19]:


# plotly.plot(df_piv['tau'], df_piv['objective'])

# Create a trace
trace = go.Scatter(
    x = df_piv['tau'],
    y = df_piv['objective']
)

data = [trace]

# Edit the layout
layout = dict(title = 'Minimal Total Cost vs. Load Constraint',
              xaxis = dict(title = 'Load Reduction (%) Lower Bound Constraint'),
              yaxis = dict(title = 'Minimal Total Cost ($)',
                           range=[0, 0.1]),
              paper_bgcolor='rgba(0,0,0,0)',
              plot_bgcolor='rgba(0,0,0,0)',
              )

fig = dict(data=data, layout=layout)
py.iplot(fig, filename='styled-line')


py.image.save_as(fig, filename='a-simple-plot_costobj.png', scale=5)


# In[12]:


fig = plt.figure(figsize=(10, 12))
ax = sns.heatmap(df_piv[df_piv.columns.difference(['tau', 'range', 'objective'])].T,
                cmap='viridis',
                cbar_kws={'label': 'acres'},
                xticklabels=list( '%d\n(%s)' % (x,"${0:,.0f}".format(y))
                                 for x,y in
                                 zip(df_piv['tau'], round(df_piv['objective'],1))
                                )
                )
plt.xlabel("loadreductionlowerbound (min total cost achieved)")

filenamestr = ''.join(['output/costobj_heatmap_tausequence_', solvername, '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname, bbox_inches='tight')


# In[28]:



print(df_piv['tau'].max(skipna=True))
print(type(df_piv['tau'].max(skipna=True)))

# print([np.nanmax(df_piv[x]) for x in list(df_piv[df_piv.columns.difference(['tau', 'range'])].columns.values)])
data = [
    go.Parcoords(
        line = dict(color = df_piv['tau'],
                    colorscale='Jet',
#                     colorscale = [[0,'#D7C16B'],[0.5,'#23D8C3'],[1,'#F3F10F']],
                   showscale=True),
        dimensions = list([
            dict(range=(0, np.nanmax(df_piv[x])), 
                 label=str(x), 
                 values=df_piv[x])
            for x in list(df_piv[df_piv.columns.difference(['tau', 'range'])].columns.values)
        ])
    )
]

layout = go.Layout(
    plot_bgcolor = '#E5E5E5',
    paper_bgcolor = '#E5E5E5',
    xaxis=dict(tickangle = 90),
)

fig = go.Figure(data = data, layout = layout)
py.iplot(fig, filename = 'parcoords-basic')


#             dict(range = [0,8],
#                 constraintrange = [4,8],
#                 label = 'Sepal Length', values = df_piv['sepal_length']),
#             dict(range = [0,8],
#                 label = 'Sepal Width', values = df_piv['sepal_width']),
#             dict(range = [0,8],
#                 label = 'Petal Length', values = df_piv['petal_length']),
#             dict(range = [0,8],
#                 label = 'Petal Width', values = df_piv['petal_width'])


# In[25]:



fig = plt.figure(figsize=(16, 8))
parallel_coordinates(df_piv.drop('range', axis=1),
                     class_column='tau', colormap='viridis')

plt.xticks(rotation=90)


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

