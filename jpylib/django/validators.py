"""
Contains custom validators that can be used throughout the SOP
"""
import re

from django.core import validators as django


domain_validator_regex_string = (
    r'#^([A-Z\d]{1}[A-Z\d-]{,62}\.)+([A-Z\d]{1}[A-Z\d-]{,62})$|'
    r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$' # ...or ip
)

domain_validator = django.RegexValidator(
    re.compile(domain_validator_regex_string, re.IGNORECASE),
    message="This is an invalid domain name. "
            "Do not include subdomain, protocol, port numbers, or any URL paths "
            "in this domain. Valid Examples: facebook.com, test.com, x.org"
)

alpha_num_begin_alpha_validator = django.RegexValidator(
    r'^[a-zA-Z][a-zA-Z0-9\-_]+$',
    message="Value must start with a letter "
            "and only contain letters, underscores, hyphens, and numbers"
)

gte_zero = django.MinValueValidator(0)
