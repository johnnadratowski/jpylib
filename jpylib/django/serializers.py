"""
Contains serializers for serializing data.
"""
import datetime
import decimal
import json

from django.db.models import Model
from django.db.models.query import ValuesQuerySet, QuerySet
from django.utils.timezone import is_aware

from jpylib.django.utils.models import model_to_dict


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that handles Django model/queryset objects in
    addition to what the default django json encoder handles
    """
    def default(self, o):

        if isinstance(o, ValuesQuerySet):
            return list(o)
        elif isinstance(o, QuerySet):
            return [model_to_dict(m) for m in o]
        elif isinstance(o, Model):
            return model_to_dict(o)
        elif isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif callable(o):
            try:
                return o()
            except:
                # If we can't get data out of the callable,
                # just return the function name
                return o.__name__
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


