__author__ = 'john'
import inspect, logging

from django.db.models import Model, FieldDoesNotExist, BooleanField

logger = logging.getLogger(__name__)

class DisplayField(object):

    def __init__(self, label, value, object=None, formatters=None):
        self.object = object
        self.label = label
        self._value = value
        self.formatters = formatters or []

    @property
    def value(self):
        val = self._get_value()
        for formatter in self.formatters:
            val = formatter(val)
        return val

    def _get_field_value(self, model, attr):
        value = getattr(model, attr)

        try:
            if isinstance(model, Model):
                field = model._meta.get_field(attr)
                if isinstance(field, BooleanField):
                    value = "Yes" if value else "No"
                elif field.choices:
                    value = dict(field.choices).get(value, value)
        except FieldDoesNotExist:
            pass

        return value

    def _get_value(self):
        # If a callable was passed in as a value, use that
        if callable(self._value):
            return self._value(self.object)

        # If a string was passed in, get value using it from the object
        if isinstance(self._value, basestring):
            try:
                val = self.object
                # Allow . access to other values
                for attr in self._value.split('.'):
                    # Check dict/list val first
                    try:
                        val = val[attr]
                    except (KeyError, IndexError, TypeError):
                        val = self._get_field_value(val, attr)

                    # Allow traversing callables
                    if callable(val):
                        val = val()

                return val

            except:
                logger.warn('Could not get value %s from object %s. Assuming static value.',
                            self._value, self.object, exc_info=True)
                return self._value

        return self._value

class FormDisplayAdapter(object):

    def __init__(self, form, object=None, include_all=False, meta=None, **kwargs):
        if object:
            self.object = object
        else:
            self.object = form.instance

        self.form = form
        self.include_all = include_all
        self.meta = meta or {}
        self._kwargs = kwargs

    def _get_meta_attr(self, attr, default=()):
        if hasattr(self.form, 'Meta') and hasattr(self.form.Meta, attr):
            return getattr(self.form.Meta, attr)

        if attr in self.meta:
            return self.meta[attr]

        return default

    def _get_field(self, field_name):
        if field_name in self.display_fields:
            field = self.display_fields[field_name]
            field.object = self.object
        else:
            field = self.form.fields[field_name]
            field = DisplayField(field.label, field_name, object=self.object)

        return field

    @property
    def display_fields(self):
        return dict(inspect.getmembers(self.form, lambda member: isinstance(member, DisplayField)))

    @property
    def fields(self):
        fields = self._get_meta_attr('display_order', self.form.fields.keys())
        exclude = self._get_meta_attr('display_exclude')

        # If we have display fields, render them in order
        for field in fields:
            # Exclude if in exclude_fields
            if field not in exclude:
                yield self._get_field(field)

        if self.include_all:
            # If we have fields not in display fields, render them afterwards.
            for field in self.form.fields:
                # Exclude if in exclude_fields or already rendered
                if field not in exclude and field not in fields:
                    yield self._get_field(field)

