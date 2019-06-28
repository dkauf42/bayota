import os
import math
import pandas as pd
import pyomo.environ as pyo

from bayom_e.src.data_handling.interface import get_loaded_data_handler_no_objective
from bayota_util.spec_handler import read_spec

from bayom_e.src.model_handling import model_expressions
from bayom_e.src.model_handling import model_components

from bayota_settings.log_setup import set_up_detailedfilelogger


class ModelHandlerBase:
    """Base Class for generating a model for the efficiency BMPs.

    Attributes:
        model ():
        specdict ():
        datahandler ():
        logger ():

    Args:
        model_spec_file (str): path to a model specification file
        geoscale (str):
        geoentities (list):
        savedata2file (bool):
        baseloadingfilename (str):
        log_level (:obj:`str`, optional): The log-level for the model generation logger. Defaults to 'INFO'.

    """
    def __init__(self, model_spec_file, geoscale, geoentities, savedata2file, baseloadingfilename='', log_level='INFO'):
        self.logger = set_up_detailedfilelogger(loggername=os.path.splitext(os.path.basename(model_spec_file))[0],
                                                filename='bayota_model_generation.log',
                                                level=log_level,
                                                also_logtoconsole=True,
                                                add_filehandler_if_already_exists=False,
                                                add_consolehandler_if_already_exists=False)

        self.specdict = read_spec(model_spec_file)

        self.datahandler = get_loaded_data_handler_no_objective(geoscale=geoscale,
                                                                geoentities=[geoentities],
                                                                savedata2file=savedata2file,
                                                                baseloadingfilename=baseloadingfilename)

        model = pyo.ConcreteModel()
        self._define_sets(model, self.datahandler, geoscale=geoscale)
        self._define_variables(model)
        self._define_params(model, self.datahandler)

        self.add_objective_from_spec(model)
        self.add_constraints_from_spec(model)

        self.add_other_components_from_spec(model)

        self.model = model

        # Add diagnostic expressions to model:
        self._add_expression_to_model(model, expr_name='original_load_for_each_loadsource_expr')
        self._add_expression_to_model(model, expr_name='new_load_for_each_loadsource_expr')

        # The model is validated.
        self.check_for_problems_in_model(model)

    def _define_sets(self, model, datahandler, geoscale):
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

        model.PLTNTS = pyo.Set(initialize=datahandler.PLTNTS,
                               ordered=True,
                               doc="""Pollutants (N, P, or S).""")

        if geoscale == 'lrseg':
            self.logger.debug('Loading lrseg geoentities')
            model.LRSEGS = pyo.Set(initialize=datahandler.LRSEGS)
        elif geoscale == 'county':
            self.logger.debug('Loading county geoentities')
            model.COUNTIES = pyo.Set(initialize=datahandler.COUNTIES)
            model.LRSEGS = pyo.Set(initialize=datahandler.LRSEGS)
            model.CNTYLRSEGLINKS = pyo.Set(initialize=datahandler.CNTYLRSEGLINKS, dimen=2)
        else:
            raise ValueError('unrecognized geoscale <%s>' % geoscale)

        model.BMPS = pyo.Set(initialize=datahandler.BMPS, ordered=True)
        model.BMPGRPS = pyo.Set(initialize=datahandler.BMPGRPS)
        model.BMPGRPING = pyo.Set(initialize=datahandler.BMPGRPING, dimen=2)

        model.LOADSRCS = pyo.Set(initialize=datahandler.LOADSRCS)

        model.BMPSRCLINKS = pyo.Set(initialize=datahandler.BMPSRCLINKS, dimen=2)
        model.BMPGRPSRCLINKS = pyo.Set(initialize=datahandler.BMPGRPSRCLINKS, dimen=2)

    @staticmethod
    def _define_variables(model):
        """ Variables """
        model.x = pyo.Var(model.BMPS,
                          model.LRSEGS,
                          model.LOADSRCS,
                          within=model.BMPSRCLINKS,
                          domain=pyo.NonNegativeReals,
                          doc='Amount of each BMP to implement.')

    @staticmethod
    def _define_params(model, datahandler):
        """ Parameters """
        # c = datahandler.c,
        # e = datahandler.eta,
        # Theta = datahandler.Theta,
        # phi = datahandler.phi,
        model.c = pyo.Param(model.BMPS,
                            initialize=datahandler.c,
                            within=pyo.NonNegativeReals,
                            doc="""cost per acre of BMP b.""")
        model.eta = pyo.Param(model.BMPS,
                              model.PLTNTS,
                              model.LRSEGS,
                              model.LOADSRCS,
                              initialize=datahandler.eta,
                              within=pyo.NonNegativeReals,
                              doc='effectiveness per acre of BMP b')
        model.phi = pyo.Param(model.LRSEGS,
                              model.LOADSRCS,
                              model.PLTNTS,
                              initialize=datahandler.phi,
                              within=pyo.NonNegativeReals,
                              doc='base nutrient load per load source')
        model.alpha = pyo.Param(model.LRSEGS,
                                model.LOADSRCS,
                                initialize=datahandler.alpha,
                                within=pyo.NonNegativeReals,
                                doc='total acres available in an lrseg/load source')

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
    def _add_expression_to_model(model, expr_name):
        try:
            model = model_expressions.__dict__[expr_name](model)  # add corresponding expression method to model object
        except KeyError as e:
            import sys
            msg = '<%s> is an unrecognized model expression' % expr_name
            raise type(e)(msg).with_traceback(sys.exc_info()[2])

        return model

    def check_for_problems_in_model(self, model):

        def original_loadsource_problems_dataframe(mdl):
            d = []
            for k, v in mdl.original_load_for_each_loadsource_expr.items():
                if math.isinf(pyo.value(v)) | math.isnan(pyo.value(v)):
                    d.append({'pollutant': k[0],
                              'loadsourceshortname': k[1],
                              'v': pyo.value(v)})

            df = pd.DataFrame(d)
            if df.empty:
                pass  # Good, no Inf's or NaN's
            else:
                df = df.sort_values('loadsourceshortname', ascending=True).reset_index()
            return df

        original_load_error = False
        # Check for Inf or NaN original loads
        for p in model.PLTNTS:
            if math.isinf(pyo.value(model.original_load_expr[p])):
                self.logger.error(f"Uh oh! original_load_expr for {p} is Inf")
                original_load_error = True
            elif math.isnan(pyo.value(model.original_load_expr[p])):
                self.logger.error(f"Uh oh! original_load_expr for {p} is NaN")
                original_load_error = True

        if original_load_error:
            self.logger.debug(original_loadsource_problems_dataframe(model).head())
