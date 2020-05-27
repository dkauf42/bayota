""" Helpful string manipulation methods used throughout the Bayota package
"""


def numstr(number, decimalpoints: int) -> str:
    """ Add commas, and restrict decimal places """
    fmtstr = '{:,.%sf}' % str(decimalpoints)
    return fmtstr.format(number)


def compact_capitalized_geography_string(s):
    """ Go from lowercase "county, state-abbrev" string to Capitalized string

    Args:
        s:

    Returns:

    Examples:
        "lancaster, pa" --> "LancasterPA"
        "anne arundel, md" --> "AnneArundelMD"
        "st. mary's, md" --> "StMarysMD"

    """
    s = s.replace(',', '').replace('.', '').replace("'", '').title().replace(' ', '')
    return s[:len(s) - 1] + s[(len(s) - 1):].capitalize()  # capitalize last letter (state abbreviation)
