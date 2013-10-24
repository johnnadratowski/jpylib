"""
Random generated helper functions.
"""

import datetime
import hashlib
import random
import time

def random_string_generator(string_length=10, alpha_only=False,
        numeric_only=False, lower_alpha_only=False, lower_numeric_only=False):
    """
    Pseudo-random generator for an alphanumeric string  of length string_length.
    For each character, randomly choose whether it will be numeric, alpha-lower,
    or alpha-upper... then chooses a random value within the ASCII 
    respective range.
    """
    current_string_length = 0
    random_string = ''
    while(current_string_length < string_length):
        if numeric_only:
            case_type = 1
        elif lower_alpha_only:
            case_type = 2
        elif lower_numeric_only:
            case_type = random.randint(1, 2)
        elif alpha_only:
            case_type = random.randint(2, 3)
        else:
            case_type = random.randint(1, 3)
        if case_type == 1:
            #Digits
            random_string = "%s%s" % (
                random_string, chr(random.randint(48, 57)))
        elif case_type == 2:
            #Lower Alpha
            random_string = "%s%s" % (
                random_string, chr(random.randint(97, 122)))
        else:
            #Upper Alpha
            random_string = "%s%s" % (
                random_string, chr(random.randint(65, 90)))
        current_string_length += 1
    return random_string

def create_unique_datetime_str():
    """
    Take the current date and time and returns a unique string that 
    can not be reproduced.
    """
    unique_datetime_str = str(time.mktime(
        datetime.datetime.now().timetuple())).split('.')[0]
    return unique_datetime_str

def generate_guid():
    """ Generates a Global Unique IDentifier. """
    return hashlib.sha1(str(random.random())).hexdigest()