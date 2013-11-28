"""
Contains helper methods for working with Django models.
"""
from jpylib.functional import item_split, filter_all


def split_field_list(fields):
    """
    Used to split model field arguments, using the
    "__" convention in django model field queries.
    :param fields: The list of arguments to split
    :return:
    """
    if not fields:
        return None, None

    output = item_split(lambda x: x.partition("__"), fields)

    output = filter_all(lambda x: x != "", output)

    return (output[0], output[2]) if output else (None, None)


