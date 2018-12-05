import pyomo.environ as pe

from efficiencysubproblem.src.data_handling.interface import get_loaded_data_handler_no_objective
from efficiencysubproblem.src.spec_handler import read_spec

from efficiencysubproblem.src.model_handling import model_expressions
from efficiencysubproblem.src.model_handling import model_components
from efficiencysubproblem.src.model_handling.utils import extract_indexed_expression_values

import logging
logger = logging.getLogger('root')


class ModelHandlerBase:
    def __init__(self, model_spec_file, geoscale, geoentities, savedata2file):

        self.specdict = read_spec(model_spec_file)

        self.datahandler = get_loaded_data_handler_no_objective(geoscale=geoscale,
                                                                geoentities=[geoentities],
                                                                savedata2file=savedata2file)

        model = pe.ConcreteModel()
        self._define_sets(model, self.datahandler, geoscale=geoscale)
        self._define_variables(model)
        self._define_params(model, self.datahandler)

        self.add_objective_from_spec(model)
        self.add_constraints_from_spec(model)

        self.add_other_components_from_spec(model)

        self.model = model

    @staticmethod
    def _define_sets(model, datahandler, geoscale):
        """ Sets """

        # pltnts = datahandler.PLTNTS,
        # counties = datahandler.COUNTIES,
        # lrsegs = datahandler.LRSEGS,
        # cntylrseglinks = datahandler.CNTYLRSEGLINKS,
        # bmps = datahandler.BMPS,
        # bmpgrps = datahandler.BMPGRPS,
        # bmpgrping = datahandler.BMPGRPING,
        # loadsrcs = datahandler.LOADSRCS,
        # bmpsrclinks = datahandler.BMPSRCLINKS,
        # bmpgrpsrclinks = datahandler.BMPGRPSRCLINKS,

        model.PLTNTS = pe.Set(initialize=datahandler.PLTNTS,
                              ordered=True,
                              doc="""Pollutants (N, P, or S).""")

        if geoscale=='lrseg':
            logger.debug('Loading lrseg geoentities')
            model.LRSEGS = pe.Set(initialize=datahandler.LRSEGS)
        elif geoscale == 'county':
            logger.debug('Loading county geoentities')
            model.COUNTIES = pe.Set(initialize=datahandler.COUNTIES)
            model.LRSEGS = pe.Set(initialize=datahandler.LRSEGS)
            model.CNTYLRSEGLINKS = pe.Set(initialize=datahandler.CNTYLRSEGLINKS, dimen=2)
        else:
            raise ValueError('unrecognized geoscale <%s>' % geoscale)

        model.BMPS = pe.Set(initialize=datahandler.BMPS, ordered=True)
        model.BMPGRPS = pe.Set(initialize=datahandler.BMPGRPS)
        model.BMPGRPING = pe.Set(initialize=datahandler.BMPGRPING, dimen=2)

        model.LOADSRCS = pe.Set(initialize=datahandler.LOADSRCS)

        model.BMPSRCLINKS = pe.Set(initialize=datahandler.BMPSRCLINKS, dimen=2)
        model.BMPGRPSRCLINKS = pe.Set(initialize=datahandler.BMPGRPSRCLINKS, dimen=2)

    @staticmethod
    def _define_variables(model):
        """ Variables """
        model.x = pe.Var(model.BMPS,
                         model.LRSEGS,
                         model.LOADSRCS,
                         within=model.BMPSRCLINKS,
                         domain=pe.NonNegativeReals,
                         doc='Amount of each BMP to implement.')

    @staticmethod
    def _define_params(model, datahandler):
        """ Parameters """
        # c = datahandler.c,
        # e = datahandler.E,
        # tau = datahandler.tau,
        # phi = datahandler.phi,
        model.c = pe.Param(model.BMPS,
                           initialize=datahandler.c,
                           within=pe.NonNegativeReals,
                           doc="""cost per acre of BMP b.""")
        model.E = pe.Param(model.BMPS,
                           model.PLTNTS,
                           model.LRSEGS,
                           model.LOADSRCS,
                           initialize=datahandler.E,
                           within=pe.NonNegativeReals,
                           doc='effectiveness per acre of BMP b')
        model.phi = pe.Param(model.LRSEGS,
                             model.LOADSRCS,
                             model.PLTNTS,
                             initialize=datahandler.phi,
                             within=pe.NonNegativeReals,
                             doc='base nutrient load per load source')
        model.T = pe.Param(model.LRSEGS,
                           model.LOADSRCS,
                           initialize=datahandler.T,
                           within=pe.NonNegativeReals,
                           doc='total acres available in an lrseg/load source')

    def add_objective_from_spec(self, model):

        # OBJECTIVE NAME
        objectivename = self.specdict['objective']['name']
        # SENSE
        if self.specdict['objective']['sense'] in ['min', 'minimize', 'minimum']:
            sense = pe.minimize
        elif self.specdict['objective']['sense'] in ['max', 'maximize', 'maximum']:
            sense = pe.maximize
        else:
            raise ValueError('unrecognized objective sense <%s>' % self.specdict['objective']['sense'])
        # EXPRESSION
        expr = self.specdict['objective']['expression']

        # BUILD THE OBJECTIVE
        logger.info('Loading objective {name="%s"} into the model object ' % objectivename)
        model = self._add_expression_to_model(model, expr_name=expr)

        # model.component(expr).pprint()
        # model.component(expr)

        # def obj_rule(*args):
        #     model = args[0]
        #     indices = model.component(expr)._index
        #     print(indices)
        #     model.component(expr)(args)
        #     return model
        #
        # model.Objective = pe.Objective(model.component(expr)._index,
        #                                rule=lambda *m_with_indices: obj_rule(m_with_indices), sense=sense)

        # expr = 'my_expression_'
        # print(model.component(expr)._index)
        # print(extract_indexed_expression_values(model.component(expr)))

        # Check if component is scalar (i.e. isn't indexed over any Sets)
        if model.component(expr)._index == {None}:
            objective_object = pe.Objective(rule=lambda m: m.component(expr),
                                            sense=sense)
        else:
            objective_object = pe.Objective(model.component(expr)._index,
                                            rule=lambda *m_with_indices: m_with_indices[0].component(expr)[m_with_indices[1:]],
                                            sense=sense)

        setattr(model, objectivename, objective_object)
        #
        #     """ Deactivate unused P and S objectives """
        #     # Retain only the Nitrogen load objective, and deactivate the others
        #     model.PercentReduction['P'].deactivate()
        #     model.PercentReduction['S'].deactivate()

    def add_constraints_from_spec(self, model):
        for i, c in enumerate(self.specdict['constraints']):

            # CONSTRAINT NAME
            constraint_name = c['name']
            # BOUND
            boundtype = c['bound']
            # BOUND PARAMETER
            boundparamname = c['boundparamname']
            # EXPRESSION
            expr = c['expression']

            # BUILD THE CONSTRAINT
            logger.info('Loading constraint #%d:{name="%s"} into the model object '
                        'with "%s" bound defined by <%s> parameter' %
                        (i, constraint_name, boundtype, boundparamname))
            model = self._add_expression_to_model(model, expr_name=expr)

            if not model.component(boundparamname):  # check if parameter already exists in model object
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    boundparamobj = pe.Param(initialize=0,
                                             within=pe.NonNegativeReals,
                                             mutable=True)
                else:
                    boundparamobj = pe.Param(model.component(expr)._index,
                                             initialize=0,
                                             within=pe.NonNegativeReals,
                                             mutable=True)
                setattr(model, boundparamname, boundparamobj)
            else:
                logger.info('parameter <%s> already exists in model object' % boundparamname)

            if boundtype == 'lower':
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    cobj = pe.Constraint(rule=lambda m: (m.component(boundparamname),
                                                         m.component(expr),
                                                         None))
                else:
                    cobj = pe.Constraint(model.component(expr)._index,
                                         rule=lambda *m_with_indices: (m_with_indices[0].component(boundparamname)[m_with_indices[1:]],
                                                                       m_with_indices[0].component(expr)[m_with_indices[1:]],
                                                                       None))
            elif boundtype == 'upper':
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    cobj = pe.Constraint(rule=lambda m: (None,
                                                         m.component(expr),
                                                         m.component(boundparamname)))
                else:
                    cobj = pe.Constraint(model.component(expr)._index,
                                         rule=lambda *m_with_indices: (None,
                                                                       m_with_indices[0].component(expr)[m_with_indices[1:]],
                                                                       m_with_indices[0].component(boundparamname)[m_with_indices[1:]]))
            else:
                raise ValueError('unrecognized bound type <%s>' % boundtype)

            setattr(model, constraint_name, cobj)

    def add_other_components_from_spec(self, model):
        for i, c in enumerate(self.specdict['other_components']):
            # COMPONENT
            component_name = c['name']

            # BUILD THE CONSTRAINT
            logger.info('Loading component #%d:{name="%s"} into the model object' % (i, component_name))
            model = self._add_component_to_model(model, comp_name=component_name)

    @staticmethod
    def _add_component_to_model(model, comp_name):
        try:
            model = model_components.__dict__[comp_name](model)  # add corresponding expression method to model object
        except KeyError as e:
            import sys
            msg = '<%s> is an unrecognized model expression' % comp_name
            raise type(e)(msg).with_traceback(sys.exc_info()[2])

        return model

    @staticmethod
    def _add_expression_to_model(model, expr_name):
        try:
            model = model_expressions.__dict__[expr_name](model)  # add corresponding expression method to model object
        except KeyError as e:
            import sys
            msg = '<%s> is an unrecognized model expression' % expr_name
            raise type(e)(msg).with_traceback(sys.exc_info()[2])

        return model
