from django.db import models
from django.utils import simplejson

from datetime import datetime

class JSONDictField(models.TextField):
    def to_python(self, value):
        if isinstance(value, basestring):
            return simplejson.loads(value)
        return value

    def get_db_prep_save(self, value, connection):
        return simplejson.dumps(value)


class JSONListField(models.TextField):
    def to_python(self, value):
        if isinstance(value, basestring):
            return simplejson.loads(value)
        return value

    def get_db_prep_save(self, value, connection):
        return simplejson.dumps(value)
    
FACEBOOK_DATEFORMAT = '%Y-%m-%dT%H:%M:%S+0000'
FACEBOOK_FALLBACK_DATEFORMAT = '%Y-%m-%dT%H:%M:%S'

class FBDateField(models.DateTimeField):
    """ Datetime field that can be assigned dates in the format
    used by the Facebook Graph API """
    def to_python(self, value):
        """ Turns a value (possibly a string) into a datetime value.

        PARAMS:
            value   the value to be converted

        RETURNS:
            a datetime object
        """
        if isinstance(value, basestring):
            try:
                return datetime.strptime(value, FACEBOOK_DATEFORMAT)
            except ValueError:
                return datetime.strptime(value[:19], FACEBOOK_FALLBACK_DATEFORMAT)
        return super(FBDateField, self).to_python(value)

    def get_db_prep_save(self, value,connection):
        """ Prepare a date value for the database. This may consist of
        serializing a datetime object, or converting a facebook-formatted
        date to one the database will understand.

        PARAMS:
            value   the value to be converted

        RETURNS:
            a string that the database can parse as a date
        """
        return super(FBDateField, self).get_db_prep_save(self.to_python(value), connection)
    
Twitter_DATEFORMAT = '%a %b %d %H:%M:%S +0000 %Y'

class TWDateField(models.DateTimeField):
    """ Datetime field that can be assigned dates in the format
    used by the Facebook Graph API """
    def to_python(self, value):
        """ Turns a value (possibly a string) into a datetime value.

        PARAMS:
            value   the value to be converted

        RETURNS:
            a datetime object
        """
        if isinstance(value, basestring):
            try:
                return datetime.strptime(value, Twitter_DATEFORMAT)
            except ValueError:
                pass
        return super(TWDateField, self).to_python(value)

    def get_db_prep_save(self, value,connection):
        """ Prepare a date value for the database. This may consist of
        serializing a datetime object, or converting a facebook-formatted
        date to one the database will understand.

        PARAMS:
            value   the value to be converted

        RETURNS:
            a string that the database can parse as a date
        """
        return super(TWDateField, self).get_db_prep_save(self.to_python(value),connection)

