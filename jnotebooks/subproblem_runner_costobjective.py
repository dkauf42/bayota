
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


# In[47]:


for index in mdl.x:
    mdl.x[index].value=-1
#             x_value = oe.value(v[index])


# In[40]:


# mdl.x.pprint()


# ## Solve problem instance

# In[52]:


myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)
merged_df = myobj.solve()
print('\nObjective is: %d' % oe.value(mdl.Total_Cost))


# In[49]:


output_file_name = 'ipopt_output_file'  # defined in the ipopt.opt file
#output_file_name = 'test_ipopt_output_file.txt'

dict_of_iterates = myobj.parse_output_file(output_file_name)


# In[43]:


dict_of_iterates.keys()


# In[50]:


varvals = {}
varvals[0] = []
for ii in dict_of_iterates.keys():
    df = dict_of_iterates[ii]
#     display(df.head(5))
    val = float(df.loc[(df.outputname=='curr_x') &
                       (df.varname=='x') & 
                       (df.index.get_level_values('varindex')=='[ConPlan,N42071SL2_2410_2700,pas]')]['value'][0])
#     print(val)
    varvals[0].append(val)

varvals[1] = []
for ii in dict_of_iterates.keys():
    df = dict_of_iterates[ii]
    varvals[1].append(float(df.loc[(df.outputname=='curr_x') &
                                   (df.varname=='x') & 
                                   (df.index.get_level_values('varindex')=='[UrbanNMPlanHR,N42071SL2_2410_2700,ntg]')]['value'][0]))


# In[51]:


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
rects = plt.scatter(varvals[0], varvals[1], c=range(len(varvals[1])))
ax = plt.gca()
plt.colorbar()
plt.xlabel('varvals[0]')
plt.ylabel('varvals[1]')


# ## Visualize

# In[46]:


merged_df.tail(50)


# In[ ]:


for l in mdl.LRSEGS:
    for p in mdl.PLTNTS:
        print('%s: %d' % (mdl.TargetPercentReduction[l,p], oe.value(mdl.TargetPercentReduction[l,p].body)))


# In[ ]:


# ---- Make zL Figure ----
filenamestr = ''.join(['output/costobj_zL_tau', taustr, '_', solvername, '_',
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                       '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

zL_bars(df=merged_df, instance=mdl,
        savefig=True, savefilepathandname=savefilepathandname)


# In[ ]:


# ---- Acres Figure ----
sorteddf_byacres = merged_df.sort_values(by='acres')

filenamestr = ''.join(['output/costobj_x_tau', taustr, '_', solvername, '_',
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'), '.png'])
savefilepathandname = os.path.join(projectpath, filenamestr)

objstr = ''.join(['Objective is: ', str(round(mdl.Total_Cost(), 2))])
titlestr = '\n'.join([objstr, 'labels are (cost per unit, total bmp instance cost)'])

acres_bars(df=sorteddf_byacres, instance=mdl, titlestr=titlestr,
           savefig=True, savefilepathandname=savefilepathandname)


# ## Gradient, Jacobian, Hessian

# In[ ]:


gjh_filename, g = gjh_solve(instance=mdl,
                            keepfiles=True,
                            amplenv=ampl,
                            basegjhpath=os.getcwd())

g_df = make_df(instance=mdl, filterbydf=merged_df, g=g)

g_df = sorteddf_byacres.merge(g_df, how='left',
                              on=['bmpshortname', 'landriversegment', 'loadsource'],
                              sort=False)


# In[ ]:


# ---- Make gradient Figure ----
# g_df_filtered = g_df.loc[abs(g_df['g'])>0.001,:].copy()
g_df_filtered = g_df
# sorteddf = g_df_filtered.sort_values(by='g')
# sorteddf_byacres

# sorteddf_byacres
# g_df = g_df.merge(sorteddf_byacres, how='right',
#                on=['bmpshortname', 'landriversegment', 'loadsource'])

keystrs = [str([x, y]) for x, y in zip(g_df_filtered['bmpshortname'], g_df_filtered['loadsource'])]
# Make Figure
fig = plt.figure(figsize=(10, 4))
rects = plt.barh(y=keystrs, width=g_df_filtered['g'])
ax = plt.gca()

ax.set_position([0.3,0.1,0.5,0.8])


filenamestr = ''.join(['output/costobj_g_tau', taustr, '_', solvername, '_',
                       datetime.now().strftime('%Y-%m-%d_%H%M%S'),
                       '.png'])
plt.savefig(os.path.join(projectpath, filenamestr))


# In[ ]:


# #Read number of variables and constraints
# nl_file = open(''.join([filecode, '.pyomo.nl']),'r')
# nl_lines = nl_file.readlines()
# num_variables = int(nl_lines[1].split(' ')[1])
# num_constraints = int(nl_lines[1].split(' ')[2])


# In[ ]:


for v in mdl.component_objects(oe.Var, active=True):
    print ("Variable component object",v)
    i=0
    for index in v:
        try:
            x_value = oe.value(v[index])
            i+=1
            try:
                print (i,"   ", index, v[index].value, g[i])
            except:
                print (i,"   ", index, v[index].value)
        except:
            pass


# In[ ]:


# #Read number of variables and constraints
# gjh_file = open(''.join([filecode, '.pyomo.gjh']),'r')
# gjh_lines = gjh_file.readlines()


# In[ ]:


# print(gjh_lines[1])


# In[ ]:


# num_variables = int(gjh_lines[1].split(' ')[1])
# num_constraints = int(gjh_lines[1].split(' ')[2])


# In[ ]:


# #Read gjh output file
# gjh = oe.AbstractModel()
# # gjh.n_var = oe.Set(initialize=range(1,num_variables+1))
# # gjh.n_cons = oe.Set(initialize=range(1,num_constraints+1))
# # gjh.g = oe.Param(gjh.n_var, default=0)
# # gjh.J = oe.Param(gjh.n_cons, gjh.n_var, default=0)
# # gjh.H = oe.Param(gjh.n_var, gjh.n_var, default=0)
# # os.rename(''.join([filecode, '.pyomo.gjh']), ''.join([filecode, '.pyomo.gjh.dat']))
# gjh_ins = gjh.create_instance(''.join([filecode, '.pyomo.gjh.dat']))

# #Print
# for i in gjh_ins.n_var:
#     print(gjh_ins.g[i])

