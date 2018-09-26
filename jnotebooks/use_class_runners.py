
# coding: utf-8

# In[2]:


_project_root = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/'         'CRC_ResearchScientist_Optimization/Optimization_Tool/'         '2_ExperimentFolder/bayota/'
_package_root = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/'         'CRC_ResearchScientist_Optimization/Optimization_Tool/'         '2_ExperimentFolder/bayota/efficiencysubproblem/'
import sys
if _project_root not in sys.path:
    sys.path.append(_project_root)  # allow this notebook to find equal-level directories
if _package_root not in sys.path:
    sys.path.append(_package_root)  # allow this notebook to find equal-level directories

from src.study import Study


# In[7]:


s = Study(objectivetype='costmin',
          geoscale='county', geoentities=['Calvert, MD'],
          baseconstraint=3)


# In[4]:


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

