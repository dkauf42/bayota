""" List the BMPs that will be excluded from the efficiency BMP model """


def excluded_bmps_list() -> list:
    """

    Reasons for each BMP:
        conservlandscape -- has a negative cost per unit

    Returns:
        list

    """
    my_list = ['conservlandscape']
    return my_list
