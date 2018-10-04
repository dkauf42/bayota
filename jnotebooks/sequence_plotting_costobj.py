
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories

import os
import pandas as pd
import seaborn as sns
import plotly.plotly as py
import plotly.graph_objs as go

get_ipython().run_line_magic('pylab', 'inline')
# from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from util.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars

_project_root = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/'         'CRC_ResearchScientist_Optimization/Optimization_Tool/'         '2_ExperimentFolder/bayota/'
_package_root = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/'         'CRC_ResearchScientist_Optimization/Optimization_Tool/'         '2_ExperimentFolder/bayota/efficiencysubproblem/'


# #### Load Solution Sequence

# In[2]:


# filename = 'output/20180904-county-NorthumberlandVA_costobj-sequence/costobj_tausequence_alldfs_ipopt_2018-09-04_141616.csv'
filename = 'output/output_study_costmin_countytausequence8_tau9_2018-10-03_113849.csv'
df = pd.read_csv(os.path.join(_package_root, filename))
# display(df.head(2))
df.shape


# In[3]:


grouped = df.groupby(by=['bmpshortname', 'loadsource'])
len(grouped)
    


# #### Pivot table for acres

# In[4]:


# df['x'].head(5)
df['x'].tail(5)


# In[6]:


df_piv = df.pivot(index='tau', columns='x', values='acres')
df_piv.reset_index(level=['tau'], inplace=True)  # make tau into a regular column
df_piv['range']=df_piv.drop('tau', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
df_piv['objective'] = df_piv['tau'].map(dict(zip(df.tau,df.solution_objectives)))  # solution_objectives
# df_piv.head(2)

# df_piv = df.pivot(index='startpointiterate', columns='x', values='acres')
# display(df_piv.head(2))
# df_piv.reset_index(level=['startpointiterate'], inplace=True)  # make tau into a regular column
# display(df_piv.head(2))
# df_piv['range']=df_piv.drop('startpointiterate', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
# display(df_piv.head(2))
# df_piv['objective'] = df_piv['startpointiterate'].map(dict(zip(df.startpointiterate,df.solution_objectives)))  # solution_objectives
# display(df_piv.head(2))

display(df_piv.shape)


# In[ ]:


# df_piv['objective'].isnan()
# df['tau'].isnull().values.any()
# print(dict(zip(df.tau,df.solution_objectives)))

display(df_piv.head(5))


# #### Pivot table for gradient (g), if available

# In[ ]:


if 'g' in df.columns:
    df_g_piv = df.pivot(index='tau', columns='x', values='g')
    df_g_piv.reset_index(level=['tau'], inplace=True)  # make tau into a regular column
    df_g_piv['range']=df_g_piv.drop('tau', axis=1).apply(lambda x : list((0, int(math.ceil(np.nanmax(x))+1))), 1)
    df_g_piv['objective'] = df_g_piv['tau'].map(dict(zip(df.tau,df.solution_objectives)))  # solution_objectives
    # df_g_piv.head(2)
else:
    print("skipping because no column 'g'")


# In[ ]:


df[['bmpshortname','landriversegment','totalinstancecost']]


# In[ ]:


grouped = df.groupby(['landriversegment', 'tau'])['totalinstancecost'].sum()
display(grouped.head(20))


# # Visualizations

# In[ ]:


from efficiencysubproblem.src.vis.sequence_plot import plotly_costobj
from efficiencysubproblem.src.vis.acres_heatmap import heatmap_costobj


# In[ ]:


# fig = plotly_costobj(df=df_piv, xname='startpointiterate')
fig = plotly_costobj(df=df_piv, xname='tau')
py.iplot(fig, filename='styled-line')


# In[ ]:


# Get costs of tau sequence for each lrseg
grped = df.groupby(['landriversegment', 'tau'])['totalinstancecost'].sum()

xname = 'tau'
title='Minimal Total Cost vs. Load Constraint'
xlabel='Load Reduction (%) Lower Bound Constraint'
ylabel='Minimal Total Cost ($)'

#Create a trace
county_trace = go.Scatter(x=df_piv[xname],
                   y=df_piv['objective'],
                          name='County'
                   )

lrseglist = list(set(df.landriversegment))
traces = [county_trace]
for l in lrseglist:
#     print(l)
#     display(grped.loc[l].tolist())
    
    traces.append(go.Scatter(x=grped.index.get_level_values('tau'),
                             y=grped.loc[l].tolist(), # marker={'color': 'blue', 'symbol': 'star', 'size': 10},
                        mode='line', name=l)
                 )
# data = [trace, trace2]
# data = [trace2]
data = traces

# Edit the layout
layout = dict(title=title,
              xaxis=dict(title=xlabel,
                         tickformat='.2f'),
              yaxis=dict(title=ylabel,
                         tickformat='.2f'),
              paper_bgcolor='rgba(0,0,0,0)',
              plot_bgcolor='rgba(0,0,0,0)',
              )

fig = dict(data=data, layout=layout)
# fig.append_trace(trace2, 1, 1)
py.iplot(fig, filename='styled-line')


# In[ ]:


asdkjhagsf


# In[ ]:


# Filepath to save to
timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
# filenamestr = ''.join(['output/costobj_heatmap_difstartpoints_', 'ipopt', '_',
#                            timestamp, '.png'])
filenamestr = ''.join(['output/costobj_heatmap_tausequence_', 'ipopt', '_',
                           timestamp, '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

# heatmap_costobj(df=df_piv, savefilepathandname=None, xname='startpointiterate')
heatmap_costobj(df=df_piv, figsize=(10,100),
                savefilepathandname=savefilepathandname, xname='tau')


# In[ ]:


sns.set_style("whitegrid", {'axes.edgecolor': '.8',
                            'axes.spines.right': False,
                            'axes.spines.top': False,
                            'grid.linestyle': ':'})

# Calculate the maximum, so we can set the yaxis limit to it
max_acres = 0
all_bmps = set()
for tauno in range(1, 10):
    df2 = df[df['tau']==tauno].groupby(by=['landriversegment', 'bmpshortname'])[['acres']].sum().unstack('bmpshortname').fillna(0)
    
    # For stacked bar graph
    currmax = df2.sum(axis=1).max()
    # For non-stacked
#     currmax = ceil(df2.values.max())
    if currmax > max_acres:
        max_acres = currmax
        
    [all_bmps.add(x) for x in df2.columns.get_level_values('bmpshortname')]
print(all_bmps)
# Use the nice tableau color palette
flatui = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
          "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"]
sns.set_palette(sns.color_palette(flatui))  # set the color palette

        # Make the figures
for tauno in range(1, 10):
    df2 = df[df['tau']==tauno].groupby(by=['landriversegment', 'bmpshortname'])[['acres']].sum().unstack('bmpshortname').fillna(0)
    
    # reset the column indices as regular columns
    levels = df2.columns.levels
    labels = df2.columns.labels
    df2.columns = levels[1][labels[1]]
    
    # add columns for bmps that are all zeros
    for bmpname in all_bmps:
        if bmpname not in df2:
            df2[bmpname] = 0
    df2 = df2[list(all_bmps)]  # reorder so that each tau is the same order
    
    fig = plt.figure(figsize=(12, 5))
    ax=fig.gca()
    p1 = df2.plot(ax=ax, kind='bar', stacked=True)
    ax.set_ylabel('acres')
    ax.set_title('Tau==%d' % tauno)
    ax.set_ylim([0, max_acres])
    ax.xaxis.grid(False)
    
#     print(ax.get_xlim()[1])
#     p1.patches[1].set_facecolor('b')
#     [rect.set_facecolor('b') for (i, rect) in enumerate(p1.patches) if (i%7==0)]

    # Filepath to save to
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    filenamestr = ''.join(['output/costobj_aggbars_tauno', str(tauno),'_ipopt', '_',
                               timestamp, '.png'])
    savefilepathandname = os.path.join(projectpath, filenamestr)
    plt.savefig(savefilepathandname, bbox_inches='tight')


# In[ ]:


from plotly.offline import iplot
import cufflinks as cf

cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

df2 = df[df['tau']==1].groupby(by=['landriversegment', 'bmpshortname'])[['acres']].sum().unstack('bmpshortname').fillna(0)
display(df2.head(2))
df2.iplot(kind='bar', barmode='stack', filename='stacked-bar-chart.png')
# py.image.save_as(fig, filename='a-simple-plot.png')


# In[ ]:


from matplotlib.animation import FuncAnimation
heights = {}

for tii in range(2, 10):
#     grouped = df[df['tau']==tii].groupby(by=['bmpshortname', 'landriversegment'])[['acres', 'totalinstancecost']].sum()
    df2 = df[df['tau']==tii].groupby(by=['landriversegment', 'bmpshortname'])[['acres']].sum().unstack('bmpshortname').fillna(0)
    fig = plt.figure()
    p2 = df2.plot(ax=fig.gca(), kind='bar', stacked=True)
    heights[tii-1] = [p.get_height() for p in p2.patches]
    plt.close(fig)


fig=plt.figure()
# grouped = df[df['tau']==1].groupby(by=['bmpshortname', 'landriversegment'])[['acres', 'totalinstancecost']].sum()
df2 = df[df['tau']==1].groupby(by=['landriversegment', 'bmpshortname'])[['acres']].sum().unstack('bmpshortname').fillna(0)
p1 = df2.plot(ax=fig.gca(), kind='bar', stacked=True)
plt.show()
heights[0] = [p.get_height() for p in p1.patches]

def init():
    return [p for p in p1.patches]

def animate(i):
    for rect, y in zip(p1.patches, heights[i]):
        rect.set_height(y)
    return rect,

anim = FuncAnimation(fig,animate,init_func=init,frames=9,interval=500,blit=False)

# Filepath to save to
timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
filenamestr = ''.join(['output/costobj_animation_tausequence_', 'ipopt', '_',
                           timestamp, '.mp4'])
savefilepathandname = os.path.join(projectpath, filenamestr)
anim.save(savefilepathandname, fps=2, extra_args=['-vcodec', 'libx264'])


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
unique_lrsegs = set(df.lrsegs)
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

first_x = df['tau'].min()
last_x = df['tau'].max()

max_acres = df['acres'].max()

i = {b:0 for b in unique_bmpnames}  # an empty dictionary of indices

for varname in ordered_var_names:
    selection = grouped.get_group(varname)
    display(selection.tail(5))

#     ax = axes_list.pop(0)
    bidx = unique_bmpnames.index(varname[0])
    ax = axes[bidx, i[varname[0]]]
    if i[varname[0]] == 0:
        ax.set_ylabel(varname[0], rotation=0, horizontalalignment='right')
    i[varname[0]] += 1
    axes_list.remove(ax)
    
    selection.plot(x='tau', y='acres', label=varname, ax=ax, legend=False)
    ax.fill_between(x=selection['tau'],y1=0,y2=selection['acres'],color='#cec6b9')
    
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

    max_constraint = selection['tau'].max()
    
    print(max_constraint)
    print((selection.loc[df['tau'] == max_constraint]['acres']))
    acres_value = float(selection.loc[df['tau'] == max_constraint]['acres'])
    ax.set_ylim((0, max_acres))
    ax.scatter(x=[max_constraint], y=[acres_value], s=60, clip_on=False, linewidth=0)
#     ax.annotate(str(int(gdp_value / 1000)) + "k", xy=[max_year, gdp_value], xytext=[7, -2], textcoords='offset points')

# Now use the matplotlib .remove() method to 
# delete anything we didn't use
for ax in axes_list:
    ax.remove()
    
fig.text(0.5, 0.00, 'Percent Load Reduction Lower Bound', ha='center')
    
plt.tight_layout()
plt.subplots_adjust(hspace=1)

filenamestr = ''.join(['output/costobj_smallmult_tausequence_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname)


# In[ ]:


fig = plt.figure(figsize=(16, 8))
parallel_coordinates(df_piv.drop('range', axis=1),
                     class_column='tau', colormap='viridis')

plt.xticks(rotation=90)


# In[ ]:


# Plotly Parallel Coordinates Plot (that doesn't work because the xaxis labels overlap, and there's no way to rotate them!!)

# print(df_piv['tau'].max(skipna=True))
# print(type(df_piv['tau'].max(skipna=True)))

# # print([np.nanmax(df_piv[x]) for x in list(df_piv[df_piv.columns.difference(['tau', 'range'])].columns.values)])
# data = [
#     go.Parcoords(
#         line = dict(color = df_piv['tau'],
#                     colorscale='Jet',
# #                     colorscale = [[0,'#D7C16B'],[0.5,'#23D8C3'],[1,'#F3F10F']],
#                    showscale=True),
#         dimensions = list([
#             dict(range=(0, np.nanmax(df_piv[x])), 
#                  label=str(x), 
#                  values=df_piv[x])
#             for x in list(df_piv[df_piv.columns.difference(['tau', 'range'])].columns.values)
#         ])
#     )
# ]

# layout = go.Layout(
#     plot_bgcolor = '#E5E5E5',
#     paper_bgcolor = '#E5E5E5',
#     xaxis=dict(tickangle = 90),
# )

# fig = go.Figure(data = data, layout = layout)
# py.iplot(fig, filename = 'parcoords-basic')

