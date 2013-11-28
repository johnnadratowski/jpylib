"""
Contains functional programming style methods
"""
from itertools import chain


def flatten_list(l):
    """
    Flattens the list recursively

    :param l: This list to flatten
    :return: flattened list

    >>> flatten_list([1, [2, [3, 4, [5, 6]], 7], 8, [9, 1], 2, 3])
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3]
    """
    output = []
    for item in l:
        if isinstance(item, (frozenset, list, set, tuple,)):
            output.extend(flatten_list(item))
        else:
            output.append(item)
    return output


def flatten_dict(d, concat="_"):
    """
    Flatten the dictionary, concatenating the keys
    :param d: dictionary to flatten
    :param concat: If callable, takes key and new key and should return
                   a new unique hashable object
                   If else, concatenates using add operator
    :return: Flattened dict

    >>> flatten_dict(dict(a=1, b=dict(c=2, d=dict(e=3, f1=dict(f=4)), g=dict(h=5)), j=6, k=7))
    {'a': 1, 'j': 6, 'k': 7, 'b_c': 2, 'b_d_e': 3, 'b_d_f1_f': 4, 'b_g_h': 5}
    >>> flatten_dict(dict(a=1, b=dict(c=2, d=dict(e=3))), concat=lambda k, n: k + '$' + n)
    {'a': 1, 'b$d$e': 3, 'b$c': 2}
    """

    output = {}
    for k, v in d.iteritems():

        if not isinstance(v, dict):
            output[k] = v
        else:
            flat_child = flatten_dict(v, concat=concat)
            for child_k, child_v in flat_child.iteritems():
                if callable(concat):
                    new_k = concat(k, child_k)
                else:
                    new_k = k + concat + child_k

                output[new_k] = child_v

    return output


def filter_all(fn, *l):
    """
    Runs the filter function on all items in a list of lists
    :param fn: Filter function
    :param l: list of lists to filter
    :return: list of filtered lists

    >>> filter_all(lambda x: x != "", ['a'], ['b'], [""], ["d"])
    [['a'], ['b'], [], ['d']]
    """
    return [filter(fn, lst) for lst in chain(*l)]


def item_split(split_fn, *l):
    """
    Splits lists into multiple lists based on a function
    working against each item in the list.

    NOTE: The split_fn must return the same number of rows every time,
    or it'll only take the first n items, where n is the minimum number
    of rows returned by split_fn!

    :param split_fn: Function to run to split items. # of items returned
                     maps to each list. Returning 4 items makes 4 lists
    :param l: List to split
    :return: list of lists containing the split items

    >>> item_split(lambda x: x.split('_'), ['a_b'], ['c_d'])
    [('a', 'c'), ('b', 'd')]
    >>> item_split(lambda x: x.split('_'), ['a_b'], ['c_d'], ['e'])
    [('a', 'c', 'e')]
    """
    return zip(*map(split_fn, list(chain(*l))))


def transform_keys(transform, d):
    """
    Transforms the keys in a dict.

    :param d: dictionary on which we're transforming keys
    :param transform: If method, calls with key and value, returns new key
                      If dict, maps keys to key values for new key
                      If list, only returns dict with specified keys
                      Else returns original dict

    :return: Dictionary with transformed keys

    >>> transform_keys(dict(one=1, two=2), lambda k, v: k.replace('o', '0'))
    {'tw0': 2, '0ne': 1}
    >>> transform_keys(dict(one=1, two=2), {'one': 1})
    {1: 1, 'two': 2}
    >>> transform_keys(dict(one=1, two=2), ['one'])
    {'one': 1}
    >>> transform_keys(dict(one=1, two=2), None)
    {'two': 2, 'one': 1}
    """
    if callable(transform):
        return {transform(k, v): v for k, v in d.iteritems()}
    elif isinstance(transform, dict):
        return {transform.get(k, k): v for k, v in d.iteritems()}
    elif isinstance(transform, list):
        return {k: v for k, v in d.iteritems() if k in transform}
    else:
        return d
