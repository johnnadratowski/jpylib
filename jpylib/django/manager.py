"""
Contains the base manager
"""
import inspect
import logging
from django.db import models
from django.db.models.query import QuerySet


logger = logging.getLogger(__name__)

class QueryField(object):
    """
    Query Field allows defining itself on a manager that inherits
    from Manager using a queryset that inherits from QuerySet that
    will automatically add calculated field calculations to a query.
    """

    def __init__(self, query, default=False, verbose_name=None, help_text=None):
        self.query = query
        self.default = default
        self.verbose_name = verbose_name
        self.help_text = help_text

class QuerySet(QuerySet):
    """
    Base Queryset
    """
    def __init__(self, model=None, query=None, using=None):
        super(QuerySet, self).__init__(model=model, query=query, using=using)
        self._select_default_fields()

    def _select_default_fields(self):
        extra = {
            field:member.query
            for field, member in self.get_query_fields().iteritems()
            if member.default
        }
        if extra:
            self.query.add_extra(extra, None, None, None, None, None)

    def select_extra_fields(self, fields=None, exclude=None, extra=None):
        fields = fields or self.get_query_fields().keys()
        exclude = exclude or []
        extra = extra or {}

        for field in fields:
            if field in exclude:
                continue
            extra[field] = self.get_query_fields()[field].query

        return self.extra(select=extra)

    def get_query_fields(self):
        if not hasattr(self, '_query_fields'):
            self._query_fields = {
                name:member for name, member in
                inspect.getmembers(self, lambda member: isinstance(member, QueryField))
            }

        return self._query_fields

class Manager(models.Manager):
    """
    Base Manager
    """


    queryset_model = QuerySet

    def get_query_set(self):
        return self.queryset_model(self.model, using=self._db)

