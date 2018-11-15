import pyomo.environ as pe


def extract_indexed_expression_values(indexed_expr):
    """Returns the values of an indexed expression (PYOMO object)."""
    return dict((ind, pe.value(val)) for ind, val in indexed_expr.items())  # changed for use with python3, from iteritems()
