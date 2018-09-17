
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
get_ipython().run_line_magic('pylab', 'inline')
from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from src.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars


# #### Load Solution Sequence

# In[2]:


# Iterates during solving
filename = 'output/single_CostObj_2018-09-04_133627.iters'
dict_of_iterates, iter_summary = IpoptParser().parse_output_file(os.path.join(projectpath, filename))

# # to get the nonstale variables...
# filename = 'output/costobj_difstartpts_alldfs_ipopt_2018-08-09_105005.csv'
# df = pd.read_csv(os.path.join(projectpath, filename))
# display(df.head(2))

# display(iter_summary.head(65))


# In[22]:


# for k, v in dict_of_iterates.items():
#     print(k)
#     print(type(v))
#     print(v.shape)
#     display(v.head(5))
#     if k>1:
#         break


# In[3]:


fig = plt.figure(figsize=(10, 4))
rects = plt.plot(iter_summary['iter'].astype(float), iter_summary['objective'].astype(float))
ax = plt.gca()
ax.set_ylabel('objective')
ax.set_xlabel('iteration')

# ax.set_ylim([-20, 0])
# ax.set_xlim([0, 2])


# In[4]:


fig = plt.figure(figsize=(10, 4))
rects = plt.plot(iter_summary['iter'].astype(float), iter_summary['objective'].astype(float))
ax = plt.gca()
ax.set_ylabel('objective')
ax.set_xlabel('iteration')

fig = plt.figure(figsize=(10, 4))
rects = plt.plot(iter_summary['iter'].astype(float), iter_summary['inf_pr'].astype(float))
ax = plt.gca()
ax.set_ylabel('primal infeasibility')
ax.set_xlabel('iteration')

fig = plt.figure(figsize=(10, 4))
rects = plt.plot(iter_summary['iter'].astype(float), iter_summary['inf_du'].astype(float))
ax = plt.gca()
ax.set_ylabel('dual infeasibility')
ax.set_xlabel('iteration')


# In[5]:


ordered_var_names = ['objective', 'inf_pr', 'inf_du']
ordered_var_strs = ['objective', 'primal infeasibility', 'dual infeasibility']
# ordered_yranges = [[-20,0], [0,1000], [0,100000]]
ordered_yranges = [None, None, None]
ordered_xranges = [None, None, None]

# We can ask for ALL THE AXES and put them into axes
fig, axes = plt.subplots(nrows=len(ordered_var_names),
                         ncols=1, sharex=True, sharey=False, figsize=(12, 12))
# axes_list = [item for sublist in axes for item in sublist]
axes_list = [item for item in axes]

for count, v in enumerate(ordered_var_names):
    x = iter_summary['iter'].astype(float)
    y = iter_summary[v].astype(float)
    
#     ax = axes[count, 1]
    ax = axes[count]
    ax.set_ylabel(v, rotation=0, horizontalalignment='right')
    rects = ax.plot(x, y)
#     ax.fill_between(x=x, y1=0, y2=y, color='#cec6b9')
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
    ax.spines['right'].set_visible(False)
    
    if not not ordered_xranges[count]:
        ax.set_xlim(ordered_xranges[count])
    
    if not not ordered_yranges[count]:
        ax.set_ylim(ordered_yranges[count])
    
    if count+1==len(ordered_var_names):
        ax.set_xlabel("iteration")
    else:
        ax.set_xlabel("")

    max_x = x.max()
    ax.scatter(x=[max_x], y=[y.iloc[-1]], s=60, clip_on=False, linewidth=0)

    axes_list.remove(ax)
    
# Now use the matplotlib .remove() method to 
# delete anything we didn't use
for ax in axes_list:
    ax.remove()
    
# fig.text(0.5, 0.00, 'Total Cost Upper Bound', ha='center')
    
plt.tight_layout()
plt.subplots_adjust(hspace=0.2)

filenamestr = ''.join(['output/costobj_iterates_summary_randomstart_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname)


# In[6]:


startingptrunno = 1
# display(dict_of_iterates[startingptrunno].head(2))

# create column that matches the format of varindex in dict_of_iterates, so that we can do a merge
df['matchingcol'] = list(['[%s]' % ','.join(x)
                          for x
                          in zip(df['bmpshortname'], df['landriversegment'], df['loadsource'])
                         ]
                        )
# display(df[df['startpointiterate']==startingptrunno].head(2))


# In[11]:


# 
df_list = []
colstokeep = ['bmpshortname', 'landriversegment', 'loadsource', 'totalannualizedcostperunit', 'startpointiterate', 'x', 'matchingcol']
i=0
for key, iterdf in dict_of_iterates.items():
    merged = iterdf.merge(df.loc[df['startpointiterate']==startingptrunno, colstokeep],
                          left_on='varindex',
                          right_on='matchingcol',
                          how='inner')
    merged['iterate'] = key
    # Save all of the solutions in a list
    df_list.append(merged)
    i+=1
print('# of iterates: %d' % i)
# Save the results
alliters = pd.concat(df_list, ignore_index=True)


# In[12]:


alliters.head(2)


# In[13]:


grouped = alliters.groupby(by=['outputname', 'x'])
i=0
for k, groupdf in grouped:
    if k[0]=='curr_x':
        fig = plt.figure(figsize=(10, 4))
        
        rects = plt.plot(groupdf['iterate'].astype(float), groupdf['value'].astype(float))
        ax = plt.gca()
        ax.set_ylabel('value')
        ax.set_xlabel('iteration')
        ax.set_title(k)
        
        plt.savefig(os.path.join(projectpath, ''.join([filename,'_var%d.png' % i])))
        i+=1


# In[14]:


print(list(zip(iter_summary.iter,iter_summary.objective)))


# In[15]:


curr_xdf = alliters[alliters['outputname']=='curr_x'].copy()
df_piv = curr_xdf.pivot(index='iterate', columns='x', values='value')
display(df_piv.head(2))
df_piv.reset_index(level=['iterate'], inplace=True)  # make iterate into a regular column
display(df_piv.head(2))
df_piv = df_piv.astype('float')
df_piv['range']=df_piv.drop('iterate', axis=1).astype(float).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
display(df_piv.head(2))
# display(df_piv['iterate'])
df_piv['objective'] = df_piv['iterate'].map(dict(zip(iter_summary.iter.astype(float), iter_summary.objective.astype(float))))  # solution_objectives
display(df_piv.head(2))


# In[16]:


# from vis.acres_heatmap import heatmap_loadobj
filenamestr = ''.join(['output/costobj_heatmap_iterates_variables_randomstart_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

# heatmap_loadobj(df=df_piv, xname='iterate')  # savefilepathandname=savefilepathandname

# Do it on our own here
fig = plt.figure(figsize=(10, 14))
ax = sns.heatmap(df_piv[df_piv.columns.difference(['iterate', 'range', 'objective'])].transpose(),
                 cmap='viridis',
                 cbar_kws={'label': 'acres'},
                 xticklabels=list(['%s\n(%.1f)' % ("{0:,.0f}".format(x), y)
                                   if (x % 5 == 0)
                                   else ''
                                   for x, y in
                                   zip(df_piv['iterate'], round(df_piv['objective'], 1))]
                                 )
                     )
plt.xlabel("iterate (min total cost achieved)")

plt.savefig(savefilepathandname, bbox_inches='tight')


# In[ ]:


varvals = {}
varvals[0] = []
for ii in dict_of_iterates.keys():
    dftemp = dict_of_iterates[ii]
    val = float(dftemp.loc[(dftemp.outputname=='curr_x') &
                       (dftemp.varname=='x') & 
                       (dftemp.index.get_level_values('varindex')=='[ConPlan,N51133RL0_6450_0000,pas]')]['value'][0])
#     print(val)
    varvals[0].append(val)

varvals[1] = []
for ii in dict_of_iterates.keys():
    dftemp = dict_of_iterates[ii]
    varvals[1].append(float(dftemp.loc[(dftemp.outputname=='curr_x') &
                                   (dftemp.varname=='x') & 
                                   (dftemp.index.get_level_values('varindex')=='[UrbanNMPlanHR,N51133RL0_6450_0000,ntg]')]['value'][0]))
    
varvals[2] = []
for ii in dict_of_iterates.keys():
    dftemp = dict_of_iterates[ii]
    varvals[2].append(float(dftemp.loc[(dftemp.outputname=='curr_x') &
                                   (dftemp.varname=='x') & 
                                   (dftemp.index.get_level_values('varindex')=='[HRTill,N51133RL0_6450_0000,soy]')]['value'][0]))


# In[ ]:


# Make Figure

fig = plt.figure(figsize=(10, 4))
rects = plt.plot(range(len(varvals[0])), varvals[0])
ax = plt.gca()
plt.ylabel('varvals[0]')
plt.xlabel('iteration')

fig = plt.figure(figsize=(10, 4))
rects = plt.plot(range(len(varvals[1])), varvals[1])
ax = plt.gca()
plt.ylabel('varvals[1]')
plt.xlabel('iteration')

fig = plt.figure(figsize=(10, 4))
rects = plt.plot(range(len(varvals[2])), varvals[2])
ax = plt.gca()
plt.ylabel('varvals[2]')
plt.xlabel('iteration')

fig = plt.figure(figsize=(10, 4))
rects = plt.scatter(varvals[0], varvals[1], c=range(len(varvals[1])))
ax = plt.gca()
plt.colorbar()
plt.xlabel('varvals[0]')
plt.ylabel('varvals[1]')


# #### Pivot table for acres

# In[ ]:


askdjhgaskdjhg


# In[ ]:


df_piv = df.pivot(index='startpointiterate', columns='x', values='acres')
display(df_piv.head(2))
df_piv.reset_index(level=['startpointiterate'], inplace=True)  # make tau into a regular column
display(df_piv.head(2))
df_piv['range']=df_piv.drop('startpointiterate', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
display(df_piv.head(2))
df_piv['objective'] = df_piv['startpointiterate'].map(dict(zip(df.startpointiterate,df.solution_objectives)))  # solution_objectives
display(df_piv.head(20))


# #### Pivot table for gradient (g), if available

# In[ ]:


if 'g' in df.columns:
    df_g_piv = df.pivot(index='totalcostupperbound', columns='x', values='g')
    df_g_piv.reset_index(level=['totalcostupperbound'], inplace=True)  # make totalcostupperbound into a regular column
    df_g_piv['range']=df_g_piv.drop('totalcostupperbound', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
    df_g_piv['objective'] = df_g_piv['totalcostupperbound'].map(dict(zip(df.totalcostupperbound,df.solution_objectives)))  # solution_objectives
    # df_g_piv.head(2)
else:
    print("skipping because no column 'g'")


# # Visualizations

# In[ ]:


from src.vis.sequence_plot import plotly_loadobj
from src.vis.acres_heatmap import heatmap_loadobj


# In[ ]:


filenamestr = ''.join(['output/loadobj_lineplot_difstartpts_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

fig = plotly_loadobj(df=df_piv, xname='startpointiterate',
                    title='Load reduction for different starting points',
                    xlabel='Different starting point runs',
                    savefilepathandname=savefilepathandname)
py.iplot(fig, filename='styled-line')


# In[ ]:


# Filepath to save to
filenamestr = ''.join(['output/loadobj_heatmap_difstartpts_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

heatmap_loadobj(df=df_piv, savefilepathandname=savefilepathandname, xname='startpointiterate')


# In[ ]:


# function to return ordered unique values
def f5(seq, idfun=None): 
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

combospresent = f5(zip(df.bmpshortname, df.loadsource))
unique_bmpnames = set(df.bmpshortname)
unique_lsnames = f5(df.loadsource)

nvarsperbmp = {b:None for b in unique_bmpnames}
for b in unique_bmpnames:
    nvarsperbmp[b] = len([x for x in combospresent if (x[0]==b)])
maxvarsofabmp = max(nvarsperbmp.values())
print(maxvarsofabmp)

sorted_keys = sorted(nvarsperbmp.items(), key=lambda x: x[1])
unique_bmpnames = list(x[0] for x in sorted_keys)
print(sorted_keys)


# In[ ]:


# We can ask for ALL THE AXES and put them into axes
fig, axes = plt.subplots(nrows=len(unique_bmpnames), ncols=maxvarsofabmp, sharex=True, sharey=True, figsize=(18,10))
axes_list = [item for sublist in axes for item in sublist] 


# ordered_var_names = df.groupby(by=['bmpshortname', 'loadsource'])['acres'].last().sort_values(ascending=False).index
        
from itertools import product
all_possibles = list(product(unique_bmpnames, unique_lsnames))
ordered_var_names = []
for posspair in all_possibles:
    if posspair in combospresent:
        ordered_var_names.append(posspair)

# Now instead of looping through the groupby
# you CREATE the groupby
# you LOOP through the ordered names
# and you use .get_group to get the right group
grouped = df.groupby(by=['bmpshortname', 'loadsource'])

first_x = df['totalcostupperbound'].min()
last_x = df['totalcostupperbound'].max()

max_acres = df['acres'].max()

i = {b:0 for b in unique_bmpnames}  # an empty dictionary of indices

for varname in ordered_var_names:
    selection = grouped.get_group(varname)

#     ax = axes_list.pop(0)
    bidx = unique_bmpnames.index(varname[0])
    ax = axes[bidx, i[varname[0]]]
    if i[varname[0]] == 0:
        ax.set_ylabel(varname[0], rotation=0, horizontalalignment='right')
    i[varname[0]] += 1
    axes_list.remove(ax)
    
    selection.plot(x='totalcostupperbound', y='acres', label=varname, ax=ax, legend=False)
    ax.fill_between(x=selection['totalcostupperbound'],y1=0,y2=selection['acres'],color='#cec6b9')
    ax.set_title(varname[1])
    ax.tick_params(
        which='both',
        bottom=False,
        left=False,
        right=False,
        top=False
    )
    ax.grid(linewidth=0.25)
    ax.set_xlim((first_x, last_x))
    ax.set_xlabel("")
    ax.set_xticks((first_x, last_x))
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    max_constraint = selection['totalcostupperbound'].max()
    acres_value = float(selection.loc[df['totalcostupperbound'] == max_constraint]['acres'])
    ax.set_ylim((0, max_acres))
    ax.scatter(x=[max_constraint], y=[acres_value], s=60, clip_on=False, linewidth=0)
#     ax.annotate(str(int(gdp_value / 1000)) + "k", xy=[max_year, gdp_value], xytext=[7, -2], textcoords='offset points')

# Now use the matplotlib .remove() method to 
# delete anything we didn't use
for ax in axes_list:
    ax.remove()
    
fig.text(0.5, 0.00, 'Total Cost Upper Bound', ha='center')
    
plt.tight_layout()
plt.subplots_adjust(hspace=1)

filenamestr = ''.join(['output/loadobj_smallmult_costboundsequence_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname)


# In[ ]:


# Heatmap for the gradient information (right now we're not saving that...)

fig = plt.figure(figsize=(10, 12))
ax = sns.heatmap(df_g_piv[df_g_piv.columns.difference(['totalcostupperbound', 'range', 'objective'])].transpose(),
                cmap='viridis',
                cbar_kws={'label': 'acres'},
                xticklabels=list( '%s\n(%.1f)' % ("${0:,.0f}".format(x),y)
                                 for x,y in
                                 zip(df_piv['totalcostupperbound'], round(df_piv['objective'],1))
                                )
                )
plt.xlabel("totalcostupperbound (max % load reduction achieved)")

# filenamestr = ''.join(['output/loadobj_Gheatmap_costboundsequence_', solvername, '_',
#                            datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
# savefilepathandname = os.path.join(projectpath, filenamestr)
# plt.savefig(savefilepathandname, bbox_inches='tight')


# In[ ]:


# Another plot that uses the gradient side-by-side with the acres

df_toplot = df_piv[df_piv.columns.difference(['totalcostupperbound', 'range', 'objective'])]
varnum = df_toplot.shape[1]

fig, axes = plt.subplots(varnum, 2, sharex=True, figsize=(9, 14))

for counter, columnname in enumerate(df_toplot):
    ax = axes[counter, 0]
    
#     ax.spines['top'].set_visible(False)
#     ax.spines['right'].set_visible(False)
#     ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    ax.grid(color='#D3D3D3', linestyle='-', linewidth=1)
    
    ax.plot(df_piv['totalcostupperbound'], df_piv[columnname].round(2))
    
    ax.set_ylabel(str(columnname), rotation=0, horizontalalignment='right')
    
df_toplot = df_g_piv[df_g_piv.columns.difference(['totalcostupperbound', 'range', 'objective'])]
varnum = df_toplot.shape[1]

maxv = np.nanmax(df_toplot.values)
for counter, columnname in enumerate(df_toplot):
    ax = axes[counter, 1]
    
    ax.set_ylim([0,maxv])
    
#     ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
#     ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis=u'both', which=u'both',length=0)
    ax.grid(color='#D3D3D3', linestyle='-', linewidth=1)
    
    ax.plot(df_piv['totalcostupperbound'], df_g_piv[columnname])
    
#     ax.set_ylabel(str(columnname), rotation=0, horizontalalignment='right')

