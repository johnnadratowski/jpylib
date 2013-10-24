import json
import logging

from django.views import generic as base_views
from django.http import HttpResponse, HttpResponseServerError

from django.conf import settings

from .serializers import JSONEncoder

logger = logging.getLogger(__name__)


class AngularIndex(base_views.TemplateView):
    template_name = 'angular_index.jade'

    def get_context_data(self, **kwargs):
        context = super(AngularIndex, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def render_to_response(self, context, **response_kwargs):

        path = self.request.get_full_path()

        # If this is a css file, set the proper content type
        if path.endswith('.css') or path.endswith('.styl'):
            response_kwargs['content_type'] = "text/css"

        return super(AngularIndex, self).render_to_response(context, **response_kwargs)

    def get_template_names(self):
        path = self.request.get_full_path()
        path = path.replace('/', '', 1)
        if path:
            # For CSS files, we'll try a .styl file first.  If we find the .styl file,
            # it will be compiled for development.  In production, requests for css files
            # will not come through this mechanism.
            if path.endswith('.css'):
                head, sep, _ = path.rpartition('.')
                return ['.'.join([head, 'styl']), path]
            else:
                return path
        else:
            return super(AngularIndex, self).get_template_names()


class AjaxView(base_views.View):

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            method = request.method.lower()
            if request.is_ajax():
                # Allow for specifying a method in the request GET parameters, which would
                # take the form of (http_method)_(ajax_method).  If there is no ajax_method,
                # just do (http_method)_ajax.  For example, if passing in ?&ajax_method=foo on a PUT
                # this would call the method put_foo.  If there is no ajax_method, it would
                # just be put_ajax.
                if request.REQUEST.get('ajax_method'):
                    method = method + '_' + request.REQUEST['ajax_method']
                method = method + '_' + "ajax"
            handler = getattr(self, method, self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        return handler(request, *args, **kwargs)

    def ajax_response(self, context, status=None, **kwargs):
        content_type = kwargs.get('content_type', 'application/json')
        try:
            output = self.serialize(context)
            return HttpResponse(output, status=status, content_type=content_type, **kwargs)
        except Exception as ex:
            logger.exception("An exception occurred serializing the response.")
            err = dict(error=ex.message)
            return HttpResponseServerError(self.serialize(err), content_type=content_type)

    def serialize(self, context):
        return json.dumps(context, cls=JSONEncoder)


class TemplateAjaxView(AjaxView, base_views.TemplateView):
    pass

