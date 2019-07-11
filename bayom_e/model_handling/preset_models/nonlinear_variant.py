import pyomo.environ as pyo


def build_model(dataplate, target_load=1):
    """Nonlinear variant of the efficiency BMP model

    Notes:
    - no indexing by nutrient (assumed single nutrient)
    - no indexing by agency

    """

    model = pyo.ConcreteModel()

    # *************************
    # SETS
    # *************************
    model.BMPS = pyo.Set(initialize=dataplate.BMPS, ordered=True)
    model.BMPGRPS = pyo.Set(initialize=dataplate.BMPGRPS)
    model.BMPGRPING = pyo.Set(initialize=dataplate.BMPGRPING, dimen=2)
    model.BMPSRCLINKS = pyo.Set(initialize=dataplate.BMPSRCLINKS, dimen=2)
    model.BMPGRPSRCLINKS = pyo.Set(initialize=dataplate.BMPGRPSRCLINKS, dimen=2)

    model.LRSEGS = pyo.Set(initialize=dataplate.LRSEGS)
    model.LOADSRCS = pyo.Set(initialize=dataplate.LOADSRCS)

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

    model.phi = pyo.Param(model.LRSEGS,
                          model.LOADSRCS,
                          doc='base nutrient load per load source',
                          within=pyo.NonNegativeReals,
                          initialize={(k[0], k[1]): v
                                      for k, v in dataplate.phi.items()
                                      if k[2] == 'N'},
                          mutable=True)

    model.alpha = pyo.Param(model.LRSEGS,
                            model.LOADSRCS,
                            doc='total acres available in an lrseg/load source',
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
                      model.LRSEGS,
                      model.LOADSRCS,
                      domain=pyo.NonNegativeReals,
                      doc='Amount of each BMP to implement.')

    # *************************
    # OBJECTIVE
    # *************************
    def total_cost_rule(mdl):
        """ Total Cost """
        return sum([(mdl.tau[b] * mdl.x[b, l, u])
                    for l in mdl.LRSEGS
                    for b in mdl.BMPS
                    for u in mdl.LOADSRCS])

    model.total_cost_expr = pyo.Expression(rule=total_cost_rule)
    model.Total_Cost = pyo.Objective(rule=lambda m: m.component('total_cost_expr'),
                                     sense=pyo.minimize)

    # *************************
    # EXPRESSIONS
    # *************************
    def new_load_rule(mdl):
        temp = sum([mdl.phi[l, u] * mdl.alpha[l, u] *
                    pyo.prod([(1 - sum([(mdl.x[b, l, u] / mdl.alpha[l, u]) * mdl.eta[b, l, u]
                                        if ((pyo.value(mdl.alpha[l, u]) > 1e-6) &
                                            ((b, gamma) in mdl.BMPGRPING) &
                                            ((b, u) in mdl.BMPSRCLINKS))
                                        else 0
                                        for b in mdl.BMPS]))
                              if (gamma, u) in mdl.BMPGRPSRCLINKS
                              else 1
                              for gamma in mdl.BMPGRPS])
                    for l in mdl.LRSEGS
                    for u in mdl.LOADSRCS])
        return temp

    model.new_load_expr = pyo.Expression(rule=new_load_rule)

    def original_load_rule(mdl):
        """ Original Load Expression (with lrsegs aggregated together) """
        return sum([(mdl.phi[l, u] * mdl.alpha[l, u])
                    for l in mdl.LRSEGS
                    for u in mdl.LOADSRCS])

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

    def additive_bmps_acre_bound_rule(mdl, gamma, l, u):
        temp = sum([mdl.x[b, l, u]
                    if (((b, gamma) in mdl.BMPGRPING) & ((b, u) in mdl.BMPSRCLINKS))
                    else 0
                    for b in mdl.BMPS])
        return None, temp, mdl.alpha[l, u]

    model.Available_Acres_Constraint = pyo.Constraint(model.BMPGRPS,
                                                      model.LRSEGS,
                                                      model.LOADSRCS,
                                                      rule=additive_bmps_acre_bound_rule)

    return model
