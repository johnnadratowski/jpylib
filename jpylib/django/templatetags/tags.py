"""
Unified template tags
"""
__author__ = 'john'

import logging, urllib

from django import template


logger = logging.getLogger(__name__)

register = template.Library()

@register.tag(name='get_params')
def get_params(parser, token):
    try:
        """{% get_params arg1=val1 arg2=val2 %}"""
        args = token.split_contents()[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Get params must include at least 1 parameter")
    else:
        arg_dict = {}
        for arg in args:
            key, _, val = arg.partition('=')
            arg_dict[key] = template.Variable(val)
        return GetParamsNode(arg_dict)


class GetParamsNode(template.Node):

    def __init__(self, args):
        self.args = args

    def render(self, context):
        params = '&'.join(['%s=%s' % (urllib.quote(unicode(k), safe=''),
                                      urllib.quote(unicode(v.resolve(context)), safe=''))
                           for k,v in self.args.iteritems()])
        return '?' + params
