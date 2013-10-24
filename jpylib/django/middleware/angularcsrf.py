"""
Middleware to support CSRF for an Angular Frontend
"""
import logging


logger = logging.getLogger(__name__)

class AngularCSRFMiddleware(object):
    """
    Middleware that is used to process CSRF requests from AngularJS
    """

    def process_request(self, request):
        """
        This method will process the request and add the proper headers
        so that CSRF can detect the CSRF token from Angular

        :param request: The request object from django
        :type request: HttpRequest object
        """

        try:
            # Angular will send the CSRF Token in an HTTP header called
            # "X-XSRF-Token... we'll take this value and stick it in the header
            # the csrf middleware expects the token to be in (X-CSRFToken header)
            csrf_token = request.META.get('HTTP_X_XSRF_TOKEN')
            if csrf_token:
                request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        except:
            logger.exception("An exception occurred attempting to set the CSRF Header")
            raise

        return None
