"""
Contains the Unified Base Model
"""
from django.db import models


class UnifiedModel(models.Model):
    """
    Base Model class for all Unified.  Contains implementation
    that is generic across all Models in the system.  All Models should inherit from this
    class at some point in their inheritance structure, unless otherwise deemed necessary.
    """

    def update(self, **kwargs):
        """Calls a .update method using this instances id. Useful
        for updating objects using F() objects."""
        self.__class__.objects.filter(pk=self.pk).update(**kwargs)

    def refresh_from_db(self):
        """Refreshes this instance from db"""
        from_db = self.__class__.objects.get(pk=self.pk)
        fields = self.__class__._meta.get_all_field_names()

        #for each field in Model
        for field in fields:
            try:
                #update this instances info from returned Model
                setattr(self, field, getattr(from_db, field))
            except:
                continue

    def turn_off_auto_now(self, field_name):
        """
        Turns off the auto_now functionality for this current instance's field.
        Useful for manually overriding last_modified dates

        RETURNS:
            True if field found and auto_now turned off, else False

        PARAMS:
            field_name (string):
                THe name of the field to turn off auto_now for
        """
        def auto_now_off(field):
            field.auto_now = False
        return self.run_on_field(field_name, auto_now_off)

    def turn_off_auto_now_add(self, field_name):
        """
        Turns off the auto_now_add functionality for this current instance's field.
        Useful for manually overriding created dates

        RETURNS:
            True if field found and auto_now_add turned off, else False

        PARAMS:
            field_name (string):
                THe name of the field to turn off auto_now_add for
        """
        def auto_now_add_off(field):
            field.auto_now_add = False
        return self.run_on_field(field_name, auto_now_add_off)

    def run_on_field(self, field_name, func):
        """
        Runs the given function on a field in this model instance

        RETURNS:
            True if field found and function ran, else False

        PARAMS:
            field_name (string):
                THe name of the field to run the given function on
            func (function):
                The function to run on the field
        """
        for field in self._meta.local_fields:
            if field.name == field_name:
                func(field)
                return True
        return False

    class Meta:
        abstract = True

