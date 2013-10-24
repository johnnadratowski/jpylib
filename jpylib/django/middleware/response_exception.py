"""
Middleware class implementation for the ResponseException
"""
from .django.exceptions import ResponseException


class ResponseExceptionMiddleware(object):
    """
    Middleware that allows returning a response anywhere in a request
    callstack by attaching a response to the ResponseException.
    """

    def process_exception(self, request, exception):
        """
        Processes the exceptions during a view call.  If the exception type
        is a ResponseException, it will return the HttpResponse attached to it.

        :returns: None if not a ResponseException, else the HttpResponse from the Exception.
        """
        if isinstance(exception, ResponseException):
            assert exception.response, "An HttpResponse must be attached to ResponseException"
            return exception.response
        return None
