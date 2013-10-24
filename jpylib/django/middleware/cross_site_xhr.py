"""
Middleware to support Cross-Domain XHR.
"""
from django import http
from django.conf import settings

ALL_ORIGINS = ['*', ]
ALL_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']
ALL_HEADERS = ['Content-Type', '*']
ALLOWED_CREDENTIALS = 'true'

DEFAULT_XS_SHARING = getattr(settings, 'DEFAULT_XS_SHARING', None)
XS_SHARING_ALLOWED_PATH = getattr(settings, 'XS_SHARING_ALLOWED_PATHS', {})

class CrossSiteXHR(object):
    """
    This middleware allows cross-domain XHR using the html5 postMessage API.
     
    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE

    Based off https://gist.github.com/426829
    """
    def process_request(self, request):
        """
        Processes the requests to see if they are allowed for XHR. XHR requests will
        be preceeded by a request to see which XHR methods are allowed. This handles
        that request.

        :param request: the request from Django
        :type request: HttpRequest
        """
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            return self.get_response(request, response)

        return None

    def process_response(self, request, response):
        """
        Process the responses back from XHR requests

        :param request: The request from Django
        :type request: HttpRequest
        :param response: The response we're sending back
        :type response: HttpResponse

        :returns: The response with updated headers if the XHR request is allowed
        """
        return self.get_response(request, response)

    def get_response(self, request, response):
        """
        Process the responses back from XHR requests

        :param request: The request from Django
        :type request: HttpRequest
        :param response: The response we're sending back
        :type response: HttpResponse

        :returns: The response with updated headers if the XHR request is allowed
        """

        for path, value in XS_SHARING_ALLOWED_PATH.iteritems():
            if request.path.startswith(path):

                response['Access-Control-Allow-Origin']  = ",".join(value.get('origins',
                                                                              ALL_ORIGINS))

                response['Access-Control-Allow-Methods'] = ",".join(value.get('methods',
                                                                              ALL_METHODS))

                response['Access-Control-Allow-Headers'] = ",".join(value.get('headers',
                                                                              ALL_HEADERS))

                response['Access-Control-Allow-Credentials'] = value.get('credentials',
                                                                         ALLOWED_CREDENTIALS)
                return response

        if DEFAULT_XS_SHARING:

            response['Access-Control-Allow-Origin']  = ",".join(DEFAULT_XS_SHARING.get(
                'origins',
                ALL_ORIGINS))

            response['Access-Control-Allow-Methods'] = ",".join(DEFAULT_XS_SHARING.get(
                'methods',
                ALL_METHODS))

            response['Access-Control-Allow-Headers'] = ",".join(DEFAULT_XS_SHARING.get(
                'headers',
                ALL_HEADERS))
            response['Access-Control-Allow-Credentials'] = DEFAULT_XS_SHARING.get(
                'credentials',
                ALLOWED_CREDENTIALS)

            return response

        return response
