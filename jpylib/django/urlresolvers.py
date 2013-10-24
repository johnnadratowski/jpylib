"""
Contains code that extends django's functionality for url resolvers
"""

def reverse_with_get(viewname, urlconf=None, args=None, kwargs=None,
                     prefix=None, current_app=None, get_params=None,
                     domain=None):
    """
    Reverses a URL and adds get parameters on to it
    """

    from django.core.urlresolvers import reverse
    url = reverse(viewname, urlconf=urlconf, args=args,
                  kwargs=kwargs, prefix=prefix, current_app=current_app)

    if not get_params:
        return url

    import urllib
    params = '&'.join(['%s=%s' % (urllib.quote(unicode(k), safe=''),
                                  urllib.quote(unicode(v), safe=''))
                       for k,v in get_params.iteritems()])

    url = '?'.join([url, params])

    return domain + url if domain else url

