from typing import Dict
import numpy as np
from pyomo import environ as pyo

from bayom_e.model_handling import model_components, model_expressions

import logging
default_logger = logging.getLogger(__name__)


class ModelBuilder:
    """ A parent class for those that build a version of the Efficiency BMP model

    Methods:
        build_model: Main entry, calls child-specific methods
        build_skeleton: *Overridden by subclasses*

    Attributes:
        model:
        specdict:

    """

    def __init__(self, logger=default_logger):
        """ Please see help(ModelBuilder) for more info """
        self.model = None
        self.specdict = None
        self.logger = logger

    def build_model(self, dataplate, geoscale, specdict) -> pyo.ConcreteModel:
        """

        Args:
            dataplate:
            geoscale:
            specdict:

        Returns:

        """
        model = self.build_skeleton(dataplate=dataplate, geoscale=geoscale, target_load={'N': np.Inf,
                                                                                         'P': np.Inf,
                                                                                         'S': np.Inf})

        self.specdict = specdict

        """ Build the model frame (objective, constraints, and other expressions) """
        self.add_objective_from_spec(model)
        self.add_constraints_from_spec(model)
        self.add_other_components_from_spec(model)

        self.model = model

        # Add diagnostic expressions to model:
        self._add_expression_to_model(model, expr_name='original_load_expr')
        self._add_expression_to_model(model, expr_name='original_load_for_each_loadsource_expr')
        self._add_expression_to_model(model, expr_name='new_load_for_each_loadsource_expr')

        return model

    def build_skeleton(self, dataplate, geoscale, target_load: Dict) -> pyo.ConcreteModel:
        """ overridden by children classes """
        pass

    def add_objective_from_spec(self, model):
        # OBJECTIVE NAME
        objectivename = self.specdict['objective']['name']
        # SENSE
        if self.specdict['objective']['sense'] in ['min', 'minimize', 'minimum']:
            sense = pyo.minimize
        elif self.specdict['objective']['sense'] in ['max', 'maximize', 'maximum']:
            sense = pyo.maximize
        else:
            raise ValueError('unrecognized objective sense <%s>' % self.specdict['objective']['sense'])
        # EXPRESSION
        expr = self.specdict['objective']['expression']

        # BUILD THE OBJECTIVE
        self.logger.info('Loading objective {name="%s"} into the model object ' % objectivename)
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
        # model.Objective = pyo.Objective(model.component(expr)._index,
        #                                rule=lambda *m_with_indices: obj_rule(m_with_indices), sense=sense)

        # expr = 'my_expression_'
        # print(model.component(expr)._index)
        # print(extract_indexed_expression_values(model.component(expr)))

        # Check if component is scalar (i.e. isn't indexed over any Sets)
        if model.component(expr)._index == {None}:
            objective_object = pyo.Objective(rule=lambda m: m.component(expr),
                                             sense=sense)
        else:
            objective_object = pyo.Objective(model.component(expr)._index,
                                             rule=lambda *m_with_indices: m_with_indices[0].component(expr)[m_with_indices[1:]],
                                             sense=sense)

        # Set the Objective into the model Object
        setattr(model, objectivename, objective_object)

        # INDICES TO DEACTIVATE
        #    for example, deactivate unused P and S objectives to retain only the Nitrogen load objective
        didcs = []
        try:
            didcs = self.specdict['objective']['deactivate_indices']
        except KeyError:
            self.logger.info('no objective indices to deactivate')
            pass
        for di in didcs:
            for k, valuelist in di.items():
                for v in valuelist:
                    model.component(objectivename)[v].deactivate()
                    self.logger.info('index <%s> deactivated in the model Objective' % v)

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
            self.logger.info('Loading constraint #%d:{name="%s"} into the model object '
                        'with "%s" bound defined by <%s> parameter' %
                        (i, constraint_name, boundtype, boundparamname))
            model = self._add_expression_to_model(model, expr_name=expr)

            if not model.component(boundparamname):  # check if parameter already exists in model object
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    boundparamobj = pyo.Param(initialize=0,
                                              within=pyo.NonNegativeReals,
                                              mutable=True)
                else:
                    boundparamobj = pyo.Param(model.component(expr)._index,
                                              initialize=0,
                                              within=pyo.NonNegativeReals,
                                              mutable=True)
                setattr(model, boundparamname, boundparamobj)
            else:
                self.logger.info('parameter <%s> already exists in model object' % boundparamname)

            if boundtype == 'lower':
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    cobj = pyo.Constraint(rule=lambda m: (m.component(boundparamname),
                                                          m.component(expr),
                                                          None))
                else:
                    cobj = pyo.Constraint(model.component(expr)._index,
                                          rule=lambda *m_with_indices: (m_with_indices[0].component(boundparamname)[m_with_indices[1:]],
                                                                       m_with_indices[0].component(expr)[m_with_indices[1:]],
                                                                       None))
            elif boundtype == 'upper':
                # Check if component is scalar (i.e. isn't indexed over any Sets)
                if model.component(expr)._index == {None}:
                    cobj = pyo.Constraint(rule=lambda m: (None,
                                                          m.component(expr),
                                                          m.component(boundparamname)))
                else:
                    cobj = pyo.Constraint(model.component(expr)._index,
                                          rule=lambda *m_with_indices: (None,
                                                                       m_with_indices[0].component(expr)[m_with_indices[1:]],
                                                                       m_with_indices[0].component(boundparamname)[m_with_indices[1:]]))
            else:
                raise ValueError('unrecognized bound type <%s>' % boundtype)

            setattr(model, constraint_name, cobj)

    @staticmethod
    def create_2dim_set_component(model, data_component, model_component_name):
        """ either from dictionary or tuples """
        if isinstance(data_component, dict):
            temp_list = []
            for item, grps in data_component.items():
                for g in grps:
                    temp_list.append((g, item))
            cobj = pyo.Set(initialize=temp_list, dimen=2)
            setattr(model, model_component_name, cobj)
        else:
            cobj = pyo.Set(initialize=data_component, dimen=2)
            setattr(model, model_component_name, cobj)

    def add_other_components_from_spec(self, model):
        for i, c in enumerate(self.specdict['other_components']):
            # COMPONENT
            component_name = c['name']

            # BUILD THE CONSTRAINT
            self.logger.info('Loading component #%d:{name="%s"} into the model object' % (i, component_name))
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
    def _add_expression_to_model(model, expr_name, logger=default_logger):

        # We check whether the expression is already part of the model
        try:
            att = getattr(model, expr_name)
            if att.is_constructed():
                logger.info(f"{expr_name} is already part of the model")
                return model
        except AttributeError as e:
            pass

        try:
            model = model_expressions.__dict__[expr_name](model)  # add corresponding expression method to model object
        except KeyError as e:
            import sys
            msg = '<%s> is an unrecognized or badly formed model expression' % expr_name
            raise type(e)(msg).with_traceback(sys.exc_info()[2])

        return model
