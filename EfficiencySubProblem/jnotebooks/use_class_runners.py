
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')  # allow this notebook to find equal-level directories

from src.study import Study


# In[2]:


s = Study(objectivetype='costmin',
          geoscale='lrseg', geoentities=['N51059PL7_4960_0000'],
          baseconstraint=3)


# In[ ]:


fname, df = s.go()


# In[ ]:


print(s)


# In[ ]:


s = Study(objectivetype='costmin',
          geoscale='lrseg', geoentities=['N51133RL0_6530_0000'],
          baseconstraint=12)


# In[ ]:


print(s)


# In[ ]:


output_file_names, alldfs = s.go(constraints=)
# output_file_names, alldfs = s.go_constraintsequence(constraints=[5, 12])

