
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
get_ipython().run_line_magic('pylab', 'inline')
from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from src.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars


# #### Load Solutions Sequences

# In[2]:


iterfilenames = ['costobj_startingpoint9_tau5_ipopt_2018-08-09_104951.iters',
                 'costobj_startingpoint8_tau5_ipopt_2018-08-09_104939.iters',
                 'costobj_startingpoint7_tau5_ipopt_2018-08-09_104923.iters',
                 'costobj_startingpoint6_tau5_ipopt_2018-08-09_104904.iters',
                 'costobj_startingpoint5_tau5_ipopt_2018-08-09_104848.iters',
                 'costobj_startingpoint4_tau5_ipopt_2018-08-09_104838.iters',
                 'costobj_startingpoint3_tau5_ipopt_2018-08-09_104827.iters',
                 'costobj_startingpoint2_tau5_ipopt_2018-08-09_104811.iters',
                 'costobj_startingpoint1_tau5_ipopt_2018-08-09_104800.iters']

# result = [SolveAndParse().parse_output_file(os.path.join(projectpath, 'output/', fn)) 
#           for fn in iterfilenames]
# dict_of_iterates_list, iter_summary_list = zip(*result)

dict_of_iterates_list = []
iter_summary_list = []
for fn in iterfilenames:
    print(fn)
    results = SolveAndParse().parse_output_file(os.path.join(projectpath, 'output/', fn))
    dict_of_iterates_list.append(results[0])
    iter_summary_list.append(results[1])


# In[151]:


ordered_var_names = ['objective', 'inf_pr', 'inf_du']
ordered_var_strs = ['objective', 'primal infeasibility', 'dual infeasibility']

fig, axes = plt.subplots(nrows=len(ordered_var_names),
                         ncols=1, sharex=True, sharey=False, figsize=(12, 12))
axes_list = [item for item in axes]

for count, v in enumerate(ordered_var_names):
    ax = axes[count]
    for rdf in iter_summary_list:
        x = rdf['iter'].apply(pd.to_numeric, args=('coerce',))
        y = rdf[v].astype(float)
        rects = ax.plot(x, y)

        max_x = x.iloc[-1]
        final_value = y.iloc[-1]
        ax.scatter(x=[max_x], y=[final_value], s=60, clip_on=False, linewidth=0)
    
    ax.set_ylim((0, y.max()))
    if v=='objective':
#         print('min:%f   :  max:%f' % (y.min(), y.max()))
        ax.set_ylim((2827702.9, 2827702.9+1e3)) 
    
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
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if count+1==len(ordered_var_names):
        ax.set_xlabel("iteration")
    else:
        ax.set_xlabel("")

    axes_list.remove(ax)
    
# Now use the matplotlib .remove() method to 
# delete anything we didn't use
for ax in axes_list:
    ax.remove()
    
plt.tight_layout()
plt.subplots_adjust(hspace=0.2)

filenamestr = ''.join(['output/costobj_iterates_summary_difstartpts_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname)


# In[4]:


len(dict_of_iterates_list)
iter_summary_list[0].head(5)


# In[5]:


alldflist = []
for runcount, (d, s) in enumerate(zip(dict_of_iterates_list, iter_summary_list)):
    s['iter'] = s['iter'].apply(pd.to_numeric, args=('coerce',))
    
    s['objective'] = s['objective'].apply(pd.to_numeric, args=('coerce',))
    obj_colno = s.columns.get_loc('objective')
    s['inf_pr'] = s['inf_pr'].apply(pd.to_numeric, args=('coerce',))
    inf_pr_colno = s.columns.get_loc('inf_pr')
    s['inf_du'] = s['inf_du'].apply(pd.to_numeric, args=('coerce',))
    inf_du_colno = s.columns.get_loc('inf_du')
    
    dflist = []
    for k, v in d.items():
        if (s.loc[(s['iter']==float(k)), 'inf_pr']).empty:
#             v['inf_pr'] = np.nan
            v['objective'] = s.iloc[k, obj_colno]
            v['inf_pr'] = s.iloc[k, inf_pr_colno]
            v['inf_du'] = s.iloc[k, inf_du_colno]
#             display(runcount)
#             display(k)
#             display(s.head(100))
#             display(s.iloc[k, :])
#             display(s.iloc[k, inf_pr_colno])
        else:
            v['objective'] = s.loc[(s['iter']==float(k)), 'objective'].iloc[0]
            v['inf_pr'] = s.loc[(s['iter']==float(k)), 'inf_pr'].iloc[0]
            v['inf_du'] = s.loc[(s['iter']==float(k)), 'inf_du'].iloc[0]
        v['iterate'] = k
        dflist.append(v.loc[v['outputname']=='curr_x'])
        
    df = pd.concat(dflist)
    df['run'] = runcount
    alldflist.append(df)

alldf = pd.concat(alldflist)
alldf.reset_index(level=['varindex', 'componentindex'], inplace=True)
alldf.drop(columns=['outputname', 'varname', 'componentindex'], inplace=True)
display(alldf.head(5))


# In[6]:


# alldf['runiter'] = (alldf['run'].map(str) + '.' + alldf['iterate'].map(str)).astype(float)
alldf['value'] = alldf['value'].astype(float)
alldf.head(3)


# In[7]:


# uris = alldf['runiter'].unique()
# for i, ri in enumerate(uris):
#     print(ri)
#     if i>200:
#         break
# display(len(alldf['runiter'].unique()))
# # display(alldf['runiter'].unique())


# In[8]:


copydf = alldf.copy()
copydf.set_index(['run', 'iterate', 'objective', 'inf_pr', 'inf_du', 'varindex'], inplace=True)
display(copydf.head(5))
display(copydf.shape)

alldf_stackedcorrect = copydf.unstack()
display(alldf_stackedcorrect.head(5))
display(alldf_stackedcorrect.shape)


# In[9]:


# alldf_stackedcorrect.index.to_frame()['run']


# In[10]:


from sklearn.decomposition import PCA

pca = PCA(n_components=3)
pc = pca.fit_transform(alldf_stackedcorrect)

# put the results back with the run, iterate, objective metadata...
pc_df = pd.DataFrame(data = pc, 
                     columns = ['PC1', 'PC2', 'PC3'])
pc_df.index = alldf_stackedcorrect.index
pc_df.reset_index(inplace=True)

print(pca.explained_variance_ratio_)
display(pc_df.head(5))


# In[11]:


df = pd.DataFrame({'var':pca.explained_variance_ratio_,
             'PC':['PC1','PC2', 'PC3']})
sns.barplot(x='PC',y="var", 
           data=df, color="c");


# In[12]:


pc_df.shape


# In[13]:


pc_df['objective'].min()


# In[14]:


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

colorlist = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
             '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
             '#bcbd22', '#17becf']
newclrlist = [hex2rgb(c) for c in colorlist]

clrdict = dict(zip(pc_df['run'].unique(), newclrlist))
clrsrs = pc_df['run'].map(clrdict).tolist()
clrsrs[0:10]

clrhexdict = dict(zip(pc_df['run'].unique(), colorlist))
clrhexsrs = pc_df['run'].map(clrhexdict).tolist()


# In[155]:


import re

display(pca.components_.shape)
varnames = alldf_stackedcorrect.columns.get_level_values('varindex')
    
fig = figure(figsize=(12, 10))
def myplot(score,coeff,labels=None):
    xs = score[:,0]
    ys = score[:,1]
    n = coeff.shape[0]
    scalex = 1.0/(xs.max() - xs.min())
    scaley = 1.0/(ys.max() - ys.min())
    plt.scatter(xs * scalex,ys * scaley, c = clrhexsrs)
#     plt.plot(xs * scalex, ys * scaley, linestyle='--') #, marker='o', color=clrhexsrs)
#     plt.plot(xs * scalex,ys * scaley, c = clrhexsrs, marker)
    for i in range(n):
#         varname = "Var"+str(i+1)
        norm = np.linalg.norm(np.array(coeff[i,:]))
        varname = varnames[i]
        if norm>0.1:
            result = re.match('\[([a-zA-Z]+),[^,]+,([a-zA-Z]+)\]', varnames[i])
            shortvarname = result.group(1)+':'+result.group(2)
            print('norm of <%s> is %f' % (shortvarname, norm))
            plt.arrow(0, 0, coeff[i,0], coeff[i,1],color = 'r',alpha = 0.5)
            if labels is None:
                plt.text(coeff[i,0]* 1.15, coeff[i,1] * 1.15, result.group(1), color = 'g', ha = 'center', va = 'center')
            else:
                plt.text(coeff[i,0]* 1.15, coeff[i,1] * 1.15, labels[i], color = 'g', ha = 'center', va = 'center')
# plt.xlim(-1,1)
# plt.ylim(-1,1)
plt.xlabel("PC{}".format(1))
plt.ylabel("PC{}".format(2))
plt.grid()

#Call the function. Use only the 2 PCs.
myplot(pc[:,0:2], np.transpose(pca.components_[0:2, :]))
# plt.show()

filenamestr = ''.join(['output/costobj_iterates_pca2comp_difstartpts_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname, transparent=True)


# In[28]:


subpcdf = pc_df.copy()
trace1 = go.Scatter3d(
                      x = subpcdf['PC1'],
                      y = subpcdf['PC2'],
                      z = subpcdf['PC3'],
                      mode='markers',
                      marker=dict(
                          size=16,
#                           color = subpcdf['run'],
                          color = clrhexsrs,
#                           colorscale='Viridis',
#                           colorscale=newclrlist,
                          opacity=0.5
                                  )
                      )
data = [trace1]
layout = go.Layout(title='Runs')
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='scatter-plot-with-colorscale')


# In[148]:


# subpcdf = pc_df.loc[pc_df['objective']<1000, :].copy()
subpcdf = pc_df.copy()
trace1 = go.Scatter3d(
                      x = subpcdf['PC1'],
                      y = subpcdf['PC2'],
                      z = subpcdf['PC3'],
                      mode='markers',
                      marker=dict(
                          size=16,
                          color = subpcdf['objective'],
                          colorscale='Viridis',
                          autocolorscale = False,
                          cauto=False,
                          cmin=2827702.9,
                          cmax=2827702.9+10,
                          showscale=True,
                          opacity=0.5
                                  )
                      )
data = [trace1]
layout = go.Layout(title='Objective')
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='scatter-plot-with-colorscale')


# In[135]:


trace1 = go.Scatter3d(
                      x = pc_df['PC1'],
                      y = pc_df['PC2'],
                      z = pc_df['PC3'],
                      mode='markers',
                      marker=dict(
                          size=16,
                          color = pc_df['inf_pr'],
                          colorscale='Viridis',
                          showscale=True,
                          opacity=0.5
                                  )
                      )
data = [trace1]
layout = go.Layout(title='Primal infeasibility')
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='scatter-plot-with-colorscale')


# In[18]:


trace1 = go.Scatter3d(
                      x = pc_df['PC1'],
                      y = pc_df['PC2'],
                      z = pc_df['PC3'],
                      mode='markers',
                      marker=dict(
                          size=16,
                          color = pc_df['inf_du'],
                          colorscale='Viridis',
                          showscale=True,
                          cauto=False,
                          cmin=0,
                          cmax=200000,
                          opacity=0.5
                                  )
                      )
data = [trace1]
layout = go.Layout(title='Dual infeasibility')
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='scatter-plot-with-colorscale')


# In[19]:


from sklearn.manifold import TSNE

time_start = time.time()
# perplexity should be between 5 and 50 usually. 1000 is just a go-for-it thing
tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=1000)
# Here we are deviating from the distributed method, we would
tsne_results = tsne.fit_transform(alldf_stackedcorrect.values)
print('t-SNE done! Time elapsed: {} seconds'.format(time.time()-time_start))

df_tsne = alldf_stackedcorrect.copy()
df_tsne['x-tsne'] = tsne_results[:,0]
df_tsne['y-tsne'] = tsne_results[:,1]
display(df_tsne.head(5))


# In[20]:


fig = plt.figure()
ax = plt.gca()
ax.scatter(x=df_tsne['x-tsne'], y=df_tsne['y-tsne'], s=60,
           c=df_tsne.index.get_level_values(level='run'),
           alpha=0.5, clip_on=False, linewidth=0)


# In[21]:


pca_50 = PCA(n_components=50)
pca_result_50 = pca_50.fit_transform(alldf_stackedcorrect)
print('Cumulative explained variation for 50 principal components: {}'.format(np.sum(pca_50.explained_variance_ratio_)))

# put the results back with the run, iterate, objective metadata...
pc50_df = pd.DataFrame(data = pca_result_50)
pc50_df.index = alldf_stackedcorrect.index
pc50_df.reset_index(inplace=True)

print(pca_50.explained_variance_ratio_.round(3)*100)
display(pc50_df.head(5))


# In[22]:


time_start = time.time()

# perplexity should be between 5 and 50 usually. 1000 is just a go-for-it thing
tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=1000)
# Here we are deviating from the distributed method, we would
tsne_pca_results = tsne.fit_transform(pd.DataFrame(data=pca_result_50).values)
print('t-SNE done! Time elapsed: {} seconds'.format(time.time()-time_start))

df_tsne_pca = alldf_stackedcorrect.copy()
df_tsne_pca['x-tsne'] = tsne_pca_results[:,0]
df_tsne_pca['y-tsne'] = tsne_pca_results[:,1]
display(df_tsne_pca.head(5))


# In[42]:


iterdf = pd.DataFrame({'iterate': df_tsne_pca.index.get_level_values(level='iterate'),
                       'run': df_tsne_pca.index.get_level_values(level='run')})
percent_complete = [round((i/(
                              (iterdf.loc[iterdf['run']==r]['iterate']).max()
                             )
                          ) * 100, 2)
                    for i, r in zip(iterdf['iterate'], iterdf['run'])]
display(percent_complete[:10])
df_tsne_pca['percent_complete'] = percent_complete
display(df_tsne_pca.loc[df_tsne_pca['percent_complete'] == 100, :].head(5))

# FIGURE 1
fig = plt.figure()
ax = plt.gca()
ax.scatter(x=df_tsne_pca['x-tsne'], y=df_tsne_pca['y-tsne'], s=60,
           c=df_tsne_pca['percent_complete'],
#            c=df_tsne_pca.index.get_level_values(level='inf_pr'),
           alpha=0.5, clip_on=False, linewidth=0)
xlim = ax.get_xlim()
ylim = ax.get_ylim()
ax.set_title('Multiple Run (color=percent_complete)')

filenamestr = ''.join(['output/costobj_iterates_summary_difstartpts_', 'ipopt', '_',
                           datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)
plt.savefig(savefilepathandname)

# FIGURE 2
fig = plt.figure()
ax = plt.gca()
ax.scatter(x=df_tsne_pca['x-tsne'], y=df_tsne_pca['y-tsne'], s=60,
#            c=df_tsne_pca.index.get_level_values(level='objective'),
           c = clrhexsrs, alpha=0.5, clip_on=False, linewidth=0)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Multiple Run (color=run)')

# FIGURE 3
# Plot just one run
fig = plt.figure()
ax = plt.gca()
df_run = df_tsne_pca.loc[df_tsne_pca.index.get_level_values(level='run') == 3, :]
ax.scatter(x=df_run['x-tsne'], y=df_run['y-tsne'], s=60,
           c=df_run.index.get_level_values(level='iterate'),
           alpha=0.5, clip_on=False, linewidth=0)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Single Run (color=iterate)')

# FIGURE 4
# Show just the final points
fig = plt.figure()
ax = plt.gca()
df_subset = df_tsne_pca.loc[df_tsne_pca['percent_complete'] == 100, :]
ax.scatter(x=df_subset['x-tsne'], y=df_subset['y-tsne'], s=60,
           c=df_subset.index.get_level_values(level='run'),
           alpha=0.5, clip_on=False, linewidth=0)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Final iterate of each run (color=run)')

# FIGURE 5
# Show the feasible region
fig = plt.figure()
ax = plt.gca()
df_subset = df_tsne_pca.loc[df_tsne_pca.index.get_level_values(level='inf_pr') > 0, :]
ax.scatter(x=df_subset['x-tsne'], y=df_subset['y-tsne'], s=60,
           c='b', alpha=0.5, clip_on=False, linewidth=0)
df_subset = df_tsne_pca.loc[df_tsne_pca.index.get_level_values(level='inf_pr') == 0, :]
ax.scatter(x=df_subset['x-tsne'], y=df_subset['y-tsne'], s=60,
           c='g', alpha=0.5, clip_on=False, linewidth=0)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Multiple runs (blue is inf_pr>0, red is inf_pr==0)')
plt.show()


# In[41]:


# FIGURE 6
# Show the feasible region entry point
grouped = df_tsne_pca.groupby([df_tsne_pca.index.get_level_values('run')])
newdf_list = []
for k,v in grouped:
    vals = v.index.get_level_values(level='inf_pr')
    for j in range(len(vals)):
        if vals[j] == 0:
            v.iloc[j, :]
            newdf_list.append(v.iloc[[j], :])
            break
            
            
df_entrypt = pd.concat(newdf_list)  #, ignore_index=True)
display(newdf.head(5))

# Show the feasible region
fig = plt.figure()
ax = plt.gca()
df_subset = df_tsne_pca.loc[df_tsne_pca.index.get_level_values(level='inf_pr') > 0, :]
ax.scatter(x=df_subset['x-tsne'], y=df_subset['y-tsne'], s=60,
           c='b', alpha=0.5, clip_on=False, linewidth=0)
df_subset = df_tsne_pca.loc[df_tsne_pca.index.get_level_values(level='inf_pr') == 0, :]
ax.scatter(x=df_subset['x-tsne'], y=df_subset['y-tsne'], s=60,
           c='g', alpha=0.5, clip_on=False, linewidth=0)

ax.scatter(x=df_entrypt['x-tsne'], y=df_entrypt['y-tsne'], s=60,
           c='r', alpha=0.5, clip_on=False, linewidth=0)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Multiple runs (blue is inf_pr>0, red is inf_pr==0)')
plt.show()


# ### How Random are the initial points?

# In[24]:


# display(alldf.loc[alldf['iterate']==0, :].head(5))
firstvalues = alldf.loc[alldf['iterate']==0, :][['varindex','value','run']]
# display(firstvalues.head(5))
fv_piv = firstvalues.pivot_table(index='varindex', columns='run', values='value')
display(fv_piv.head(2))
display(fv_piv.shape)
fv_piv = fv_piv.reset_index().drop(columns='varindex')
fv_stk = fv_piv.stack().reset_index().rename(columns={0: 'value'})
display(fv_stk.head(2))
display(fv_stk.shape)


# In[25]:


# x=fv_stk['level_0']
# y=fv_stk['value']
x=fv_stk.loc[fv_stk['level_0'].isin(range(100)), 'level_0']
y=fv_stk.loc[fv_stk['level_0'].isin(range(100)), 'value']

# Version 1
fig=plt.figure()
plt.scatter(x=x, y=y)

# Version 2
fig=plt.figure()
plt.hist2d(x, y, (50, 50), cmap=plt.cm.jet)
plt.colorbar()

# Version 3
from scipy.stats import gaussian_kde
# Calculate the point density
xy = np.vstack([x,y])
z = gaussian_kde(xy)(xy)
# Sort the points by density, so that the densest points are plotted last
idx = z.argsort()
# print(idx)
print(type(idx))
# x = np.array(x)[idx]
x, y, z = np.array(x)[idx], np.array(y)[idx], np.array(z)[idx]
# Make the plot
fig, ax = plt.subplots()
sc = ax.scatter(x, y, c=z, s=50, edgecolor='')
plt.colorbar(sc)
plt.show()


# In[26]:


# from plotly import tools

# cbarlocs = [.85, .5, .15]

# trace1 = go.Scatter3d(
#                     x = pc_df['PC1'],
#                     y = pc_df['PC2'],
#                     z = pc_df['PC3'],
#                     mode='markers',
#                     marker=dict(
#                         size=16,
#                         color = pc_df['objective'],
#                         colorscale='Viridis',
# #                         showscale=True,
#                         colorbar=dict(len=0.25, y=cbarlocs[0]),
#                         opacity=0.5
#                                 )
#                     )
# trace2 = go.Scatter3d(
#                     x = pc_df['PC1'],
#                     y = pc_df['PC2'],
#                     z = pc_df['PC3'],
#                     mode='markers',
#                     marker=dict(
#                         size=16,
#                         color = pc_df['inf_pr'],
#                         colorscale='Viridis',
# #                         showscale=True,
#                         colorbar=dict(len=0.25, y=cbarlocs[1]),
#                         opacity=0.5
#                                 )
#                     )
# trace3 = go.Scatter3d(
#                     x = pc_df['PC1'],
#                     y = pc_df['PC2'],
#                     z = pc_df['PC3'],
#                     mode='markers',
#                     marker=dict(
#                         size=16,
#                         color = pc_df['inf_du'],
#                         colorscale='Viridis',
# #                         showscale=True,
#                         colorbar=dict(len=0.25, y=cbarlocs[2]),
#                         opacity=0.5
#                                 )
#                     )

# fig = tools.make_subplots(rows=3, cols=1,
#                           specs=[[{'is_3d': True}], [{'is_3d': True}],
#                                  [{'is_3d': True}]])
# # fig = tools.make_subplots(rows=3, cols=1)

# fig.append_trace(trace1, 1, 1)
# fig.append_trace(trace2, 2, 1)
# fig.append_trace(trace3, 3, 1)

# fig['layout'].update(height=600, width=800, title='i <3 annotations and subplots')

# # py.iplot(fig, file_name='multiple_plots')
# py.iplot(fig, filename='3dscatter-plot-with-colorscale')


# In[27]:


# # Iterates during solving
# filename = 'output/costobj_startingpoint9_tau5_ipopt_2018-08-09_104951.iters'
# dict_of_iterates, iter_summary = SolveAndParse().parse_output_file(os.path.join(projectpath, 'output/', filename))

# # to get the nonstale variables...
# filename = 'output/costobj_difstartpts_alldfs_ipopt_2018-08-09_105005.csv'
# df = pd.read_csv(os.path.join(projectpath, filename))
# # display(df.head(2))

# display(iter_summary.head(65))

