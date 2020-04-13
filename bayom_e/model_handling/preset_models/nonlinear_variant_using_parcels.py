""" Nonlinear variant of the efficiency BMP model indexed by Parcels
"""
import pyomo.environ as pyo

from bayom_e.model_handling.builders.modelbuilder import ModelBuilder

def build_model(dataplate, target_load=1):
    """Nonlinear variant of the efficiency BMP model indexed by Parcels

    Notes:
    - no indexing by nutrient (assumed single nutrient)

    """

    model = pyo.ConcreteModel()

    # *************************
    # SETS
    # *************************
    model.PLTNTS = pyo.Set(initialize=dataplate.PLTNTS)
    model.LRSEGS = pyo.Set(initialize=dataplate.LRSEGS)
    model.LOADSRCS = pyo.Set(initialize=dataplate.LOADSRCS)
    model.AGENCIES = pyo.Set(initialize=dataplate.AGENCIES)
    model.PARCELS = pyo.Set(initialize=dataplate.PARCELS, within=model.LRSEGS*model.LOADSRCS*model.AGENCIES)

    model.BMPS = pyo.Set(initialize=dataplate.BMPS, ordered=True)
    model.BMPGRPS = pyo.Set(initialize=dataplate.BMPGRPS)

    ModelBuilder.create_2dim_set_component(model, dataplate.BMPGRPING, 'BMPGRPING')

    model.BMPSRCLINKS = pyo.Set(initialize=dataplate.BMPSRCLINKS, dimen=2)
    model.BMPGRPSRCLINKS = pyo.Set(initialize=dataplate.BMPGRPSRCLINKS, dimen=2)

    # *************************
    #  IMMUTABLE PARAMETERS
    # *************************
    model.tau = pyo.Param(model.BMPS,
                          doc="""cost per acre of BMP b ($)""",
                          within=pyo.NonNegativeReals,
                          initialize=dataplate.tau)

    model.eta = pyo.Param(model.BMPS,
                          model.LRSEGS,
                          model.LOADSRCS,
                          doc='effectiveness per acre of BMP b (unitless)',
                          within=pyo.NonNegativeReals,
                          initialize={(k[0], k[2], k[3]): v
                                      for k, v in dataplate.eta.items()
                                      if k[1] == 'N'})

    model.phi = pyo.Param(model.PARCELS,
                          doc='base nutrient load per load source',
                          within=pyo.NonNegativeReals,
                          initialize={(k[0], k[1], k[2]): v
                                      for k, v in dataplate.phi.items()
                                      if k[3] == 'N'},
                          mutable=True)

    model.alpha = pyo.Param(model.PARCELS,
                            doc='total acres available in an lrseg/loadsource/agency',
                            within=pyo.NonNegativeReals,
                            mutable=True,
                            initialize={k: v for k, v in dataplate.alpha.items()})

    # *************************
    #  MUTABLE PARAMETERS
    # *************************
    model.target_load_param = pyo.Param(initialize=target_load,
                                        mutable=True)

    # *************************
    # VARIABLES
    # *************************
    model.x = pyo.Var(model.BMPS,
                      model.PARCELS,
                      domain=pyo.NonNegativeReals,
                      doc='Amount of each BMP to implement.')

    # *************************
    # OBJECTIVE
    # *************************
    def total_cost_rule(mdl):
        """ Total Cost """
        return sum([(mdl.tau[b] * mdl.x[b, l, u, h])
                    for b in mdl.BMPS
                    for l, u, h in mdl.PARCELS])

    model.total_cost_expr = pyo.Expression(rule=total_cost_rule)
    model.Total_Cost = pyo.Objective(rule=lambda m: m.component('total_cost_expr'),
                                     sense=pyo.minimize)

    # *************************
    # EXPRESSIONS
    # *************************
    def new_load_rule(mdl):
        temp = sum([mdl.phi[l, u, h] * mdl.alpha[l, u, h] *
                    pyo.prod([(1 - sum([(mdl.x[b, l, u, h] / mdl.alpha[l, u, h]) * mdl.eta[b, l, u]
                                        if ((pyo.value(mdl.alpha[l, u, h]) > 1e-6) &
                                            ((b, gamma) in mdl.BMPGRPING) &
                                            ((b, u) in mdl.BMPSRCLINKS))
                                        else 0
                                        for b in mdl.BMPS]))
                              if (gamma, u) in mdl.BMPGRPSRCLINKS
                              else 1
                              for gamma in mdl.BMPGRPS])
                    for l, u, h in mdl.PARCELS])
        return temp

    model.new_load_expr = pyo.Expression(rule=new_load_rule)

    def original_load_rule(mdl):
        """ Original Load Expression (with lrsegs aggregated together) """
        return sum([(mdl.phi[l, u, h] * mdl.alpha[l, u, h])
                    for l, u, h in mdl.PARCELS])

    model.original_load_expr = pyo.Expression(rule=original_load_rule)

    def target_percent_reduction_rule(mdl):
        return ((mdl.original_load_expr - mdl.target_load_param) / mdl.original_load_expr) * 100
    model.target_percent_reduction_expr = pyo.Expression(rule=target_percent_reduction_rule)

    def percent_reduction_rule(mdl):
        return ((mdl.original_load_expr - mdl.new_load_expr) / mdl.original_load_expr) * 100
    model.percent_reduction_expr = pyo.Expression(rule=percent_reduction_rule)

    # *************************
    # CONSTRAINTS
    # *************************
    model.target_load_constraint = pyo.Constraint(rule=lambda m: (None,
                                                                  model.new_load_expr,
                                                                  model.target_load_param))

    def additive_bmps_acre_bound_rule(mdl, gamma, l, u, h):
        temp = sum([mdl.x[b, l, u, h]
                    if (((b, gamma) in mdl.BMPGRPING) & ((b, u) in mdl.BMPSRCLINKS))
                    else 0
                    for b in mdl.BMPS])
        return None, temp, mdl.alpha[l, u, h]

    model.Available_Acres_Constraint = pyo.Constraint(model.BMPGRPS,
                                                      model.PARCELS,
                                                      rule=additive_bmps_acre_bound_rule)

    return model
