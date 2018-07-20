from pyomo.opt import SolverFactory
from util.subproblem_model_costobjective import build_subproblem_model

# Note that there is no need to call create_instance on a ConcreteModel
mdl = build_subproblem_model(...)
solver = SolverFactory("glpk")
results = solver.solve(mdl, tee=True, symbolic_solver_labels=True)

print('Objective is:')
# print(instance.Total_Cost.expr())

# instance.solutions.store_to(results)
print(results)