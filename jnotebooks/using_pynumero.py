
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories
get_ipython().run_line_magic('pylab', 'inline')

pathtopynumero = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/pyomo'
sys.path.append(pathtopynumero)

from importing_modules import *
# pyomo.environ as oe, seaborn as sns, plotly.plotly as py, plotly.graph_objs as go
# from src.gjh_wrapper import gjh_solve, make_df, from vis import acres_bars, zL_bars


import pyomo.dae as dae
from pyomo.contrib.pynumero.sparse import BlockSymMatrix
from pyomo.contrib.pynumero.interfaces import PyomoNLP


# In[2]:


asdjhgj
# import sys

# sys.path.append('/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/pyomo')  # allow this notebook to find equal-level directories
# print('\n'.join(sys.path))


# In[ ]:


# import os
# import pyomo


# In[3]:


pyomo.__file__


# In[ ]:


pathtopynumero = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/pyomo'

# import importlib.src
# spec = importlib.src.spec_from_file_location("pyomo", pathtopynumero)
# foo = importlib.src.module_from_spec(spec)
# spec.loader.exec_module(foo)
# # foo.MyClass()


# In[ ]:



# sys.path.append('..')  # allow this notebook to find equal-level directories


# import pyomo.environ as oe
# import pyomo.dae as dae
# from pyomo.contrib.pynumero.sparse import BlockSymMatrix
# from pyomo.contrib.pynumero.interfaces import PyomoNLP


# import matplotlib.pylab as plt
# from src.subproblem_model_loadobjective import LoadObj
# from src.subproblem_solver_ipopt import SolveAndParse
# from vis.acres_bars import acres_bars
# from vis.zL_bars import zL_bars

# %pylab inline
# from datetime import datetime


# In[4]:


baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')


# ## Create a problem instance

# In[6]:


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


# In[12]:


# reinitialize the variables
for k in mdl.x:
#         mdl.x[k] = float(random.randrange(0, 600001))/100
    mdl.x[k] = round(random.uniform(0, 6000), 2)


# In[36]:


nlp = PyomoNLP(mdl)
x = nlp.x_init
res_c = nlp.evaluate_c(x)
xl = nlp.xl
xu = nlp.xu
res_d1 = nlp.evaluate_d(x)

# general inequality constraints (see: https://github.com/santiagoropb/pyomo/blob/pynumero/pyomo/contrib/pynumero/interfaces/nlp.py)
gl = nlp.gl
gu = nlp.gu
g = nlp.evaluate_g(x)
res_d2 = gu[nlp.nc:] - g[nlp.nc:]


# In[42]:


print(x)
print(len(x))
print(nlp.ng)


# In[39]:


print(len(gl))
print(len(res_d1))
print(len(res_d2))
print(res_d1[0])
print(res_d2[0])


# In[31]:


print(len(res_d))
for i in range(15):
    print(nlp.evaluate_d(x)[i])


# In[ ]:


looptimestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

myobj = SolveAndParse(instance=mdl, data=data, localsolver=localsolver, solvername=solvername)

# set filepath for saving information about all of the solver iterates
output_file_name=os.path.join(projectpath, ''.join(['output/single_LoadObj_', looptimestamp, '.iters']))
myobj.modify_ipopt_options(optionsfilepath='ipopt.opt', newoutputfilepath=output_file_name)

merged_df = myobj.solve()
print('\nObjective is: %d' % oe.value(mdl.PercentReduction['N']))


# In[ ]:


from pyomo.contrib.pynumero.examples import derivatives
# derivatives()

# Discretize model using Orthogonal Collocation
discretizer = oe.TransformationFactory('dae.collocation')
discretizer.apply_to(mdl, nfe=100, ncp=3, scheme='LAGRANGE-RADAU')
discretizer.reduce_collocation_points(mdl, var=mdl.x, ncp=1, contset=mdl.t)


# In[ ]:


# Interface pyomo model with nlp
nlp = PyomoNLP(mdl)
x = nlp.create_vector_x()
lam = nlp.create_vector_y()

# Evaluate jacobian
jac_c = nlp.jacobian_g(x)
plt.spy(jac_c)
plt.title('Jacobian of the constraints\n')
plt.show()

print(type(jac_c))
print(jac_c.shape)


# In[ ]:


jac_c


# In[ ]:


# Evaluate hessian of the lagrangian
hess_lag = nlp.hessian_lag(x, lam)
plt.spy(hess_lag)
plt.title('Hessian of the Lagrangian function\n')
plt.show()

