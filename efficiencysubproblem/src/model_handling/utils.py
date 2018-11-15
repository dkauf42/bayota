import pyomo.environ as pe

from efficiencysubproblem.src import spec_handler

def extract_indexed_expression_values(indexed_expr):
    """Returns the values of an indexed expression (PYOMO object)."""
    return dict((ind, pe.value(val)) for ind, val in indexed_expr.items())  # changed for use with python3, from iteritems()


def parse_model_spec(file):
    adict = spec_handler.read_spec(file)


    return adict