"""
Unified custom template filters
"""
from django import template


register = template.Library()

def append(value, append):
    """ 
    Django template tag filter that appends arg to the value
    if value is non-empty. Else, returns an empty string
    
    :param value: The value we're appending the text to
    :type value: string
    :param append: The string we're appending to the value
    :type append: string
    :returns: String with append value appended to it, if it's not empty. Else, an empty string
    """
    
    value = unicode(value)
    append = unicode(append)
    return  value + append if value and append else ""

register.filter('append', append)

def prepend(value, prepend):
    """ 
    Django template tag filter that prepends arg to the value 
    if value is non-empty. Else, returns an empty string 

    :param value: The value we're prepending the text to
    :type value: string
    :param prepend: The string we're prepending to the value
    :type prepend: string
    :returns: String with prepend value appended to it, if it's not empty. Else, an empty string
    """
    
    value = unicode(value)
    prepend = unicode(prepend)
    return prepend + value if value and prepend else ""

register.filter('prepend', prepend)

def dict_key(d, key_name):
    """
    Allows a developer to get a key from a dictionary by passing
    in a variable name

    :param d: The dictionary we're getting the key from
    :type d: dict
    :param key_name: The name of the key we're getting
    :returns: The value in the dict of keyname, else .. setting:: TEMPLATE_STRING_IF_INVALID
    """
    try:
        value = d[key_name]
    except KeyError:
        from django.conf import settings

        value = settings.TEMPLATE_STRING_IF_INVALID

    return value
register.filter('dict_key', dict_key)

def multiply_string(multiple, string_multiply):
    """
    Multiply a string by a number and return it.

    :param multiple: how much to multiple the string by
    :type multiple: integer
    :param string_multiply: the string we're multiplying
    :type string_multiply: string
    :returns: The properly multiplied string
    """
    try:
        value = multiple * string_multiply
    except KeyError:
        from django.conf import settings

        value = settings.TEMPLATE_STRING_IF_INVALID

    return value
register.filter('multiply_string', multiply_string)

def remove_char(value, remove_char):
    """
    Template filter that will remove the given char from teh given value

    :param value: the string we're removing the character from
    :type value: string
    :param remove_char: the character to remove from teh string
    :type remove_char: string
    :returns: String with prepend value appended to it, if it's not empty. Else, an empty string
    """
    
    value = unicode(value)
    return value.replace(remove_char, " ")

register.filter('remove_char', remove_char)
