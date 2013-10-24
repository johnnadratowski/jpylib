"""
Contains serializers for serializing data.
"""
from StringIO import StringIO
import json

from django.core.serializers.base import DeserializationError
from django.core.serializers import json as django_json, serialize
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.db.models import Model
from django.db.models.query import ValuesQuerySet, QuerySet
from django.utils.encoding import smart_unicode


class JSONEncoder(django_json.DjangoJSONEncoder):
    """
    JSONEncoder subclass that handles Django model/queryset objects in
    addition to what the default django json encoder handles
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, ValuesQuerySet):
            return super(JSONEncoder, self).default(list(o))
        elif isinstance(o, QuerySet):
            return serialize('json', o)
        elif isinstance(o, Model):
            # HACK: since the Django serializer doesn't handle model objects,
            # we pass it in as a list.  Because of this, it returns a JSON list.
            # Since it should only be one object, we should be ok just stripping
            # out the JSON array chars.
            ret_val = serialize('json', [o, ]).strip().lstrip('[').rstrip(']').strip()
            assert ret_val.endswith('}'), "Error encoding JSON object - Model should be JSON dict"
            return ret_val
        else:
            return super(JSONEncoder, self).default(o)


class DeserializedObject(object):
    """
    The DeserializedObject returned from Django's serializers bypasses the model's
    saving method, which isn't desired in this case.  This class wraps the Deserialized
    object from Django's deserializers to enable this.
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __repr__(self):
        return repr(self.wrapped)

    def save(self, force_insert=False, force_update=False, save_m2m=True, using=None):
        self.wrapped.object.save(
            force_insert=force_insert,
            force_update=force_update,
            using=using
        )
        if self.wrapped.m2m_data and save_m2m:
            for accessor_name, object_list in self.wrapped.m2m_data.items():
                setattr(self.wrapped.object, accessor_name, object_list)

        # prevent a second (possibly accidental) call to save() from saving
        # the m2m data twice.
        self.wrapped.m2m_data = None


# def deserialize(stream_or_string, **options):
#     """
#     Deserializer that is a bit more forgiving than the default Django one.  Also
#     allows for passing a 'model' into options that defines the model to deserialize
#     to.
#     """
#     if isinstance(stream_or_string, basestring):
#         stream = StringIO(stream_or_string)
#     else:
#         stream = stream_or_string
#     try:
#         output = json.load(stream)
#         if isinstance(output, dict):
#             output = [output, ]
#
#         assert isinstance(output, list), "Cannot serialize output of type %s" % type(output)
#
#         base_model = options.get('model')
#         if 'model' in options:
#             for model in output:
#                 model['model'] = smart_unicode(options['model']._meta)
#
#         import ipdb; ipdb.set_trace()
#
#         for obj in output:
#
#         for obj in PythonDeserializer(output, **options):
#             yield DeserializedObject(obj)
#     except GeneratorExit:
#         raise
#     except Exception, e:
#         # Map to deserializer error
#         raise DeserializationError(e)
