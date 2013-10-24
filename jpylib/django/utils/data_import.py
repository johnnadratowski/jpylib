"""
This module contains classes and methods that allow for importing values from
a data source into a model.
"""
import logging, datetime, time, traceback
from decimal import Decimal

from django.db import models
from django.core.exceptions import MultipleObjectsReturned


logger = logging.getLogger(__name__)

def import_text(value):
    
    if value is None:
        value = ''
        
    return value

def import_integer(value, positive=False):
    
    if value is None or value == '':
        value = 0
    
    if isinstance(value, basestring):
        value = int(Decimal(value))
        
    if positive and value < 0:
        value = 0
        
    return value

def import_datetime(value):
    
    if value is None or value == '':
        value = '1970-01-01T00:00:00.000Z'
        
    if isinstance(value, basestring):
        value = datetime.datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
    
    return value

def import_date(value):
    
    if value is None or value == '':
        value = '1970-01-01'
        
    if isinstance(value, basestring):
        value = datetime.datetime.strptime(value[:10], "%Y-%m-%d")
        
    return value
        
def import_decimal(value, positive=False):
    
    if value is None or value == '':
        value = 0.00
        
    if isinstance(value, basestring):
        value = Decimal(value)
        
    if positive and value < 0:
        value = 0.00
        
    return value
        
def import_boolean(value):
    
    if value is None or value == '':
        value = False
        
    if isinstance(value, basestring):
        value = value.lower() == 'true'
        
    return value

def import_value(model_obj, value, attr_name, field=None, **kwargs):
    """
    Given a model instance, an attribute name to update, and a value, this
    tool will transform the value to be set properly into the attribute.
    
    RETURNS:
        The updated model_obj, the cleaned value, and the field object
        
    PARAMS:
        model_obj(Model):
            A model instance to be updated with the value into attribute attr_name
        attr_name(string):
            A string specifying the attribute name to update, only needed if
            field isn't given
        field(Field object):
            The field we're updating. If we don't have this, the field will be
            retrieved using the attr_name.
        value (any):
            The value to update the model_obj attr_name with
    """
    
    transformed = value
    
    if not field:
        
        try:
            field = get_field_with_name(model_obj, attr_name)
        except models.FieldDoesNotExist:
            logger.info('Field %s on model %s not found.', attr_name, model_obj)
            raise 
    
    try:
        transformed = _transform_value_for_field(field, model_obj, value, **kwargs)
        
    except DoNotSetException:
        logger.info("Attribute name %s not set for model %s for reason %s", 
                    attr_name, 
                    model_obj,
                    traceback.print_exc())
        raise
    
    if type(transformed) == list: ### M2M fields work differently, we'll clear and add all
        attr = getattr(model_obj, attr_name)
        attr.clear() # clear old relationships so we can add all the existing ones
        attr.add(*transformed)
            
    else:
        setattr(model_obj, attr_name, transformed)
    
    return model_obj, transformed, field

def field_is_number(model_obj, attr_name, field=None, raise_unfound=False):
    """
    Given the model and the field name, determines if the field is a number field.
    
    RETURNS:
        True if this is a number field
    
    PARAMS:
        model_obj (Model Class or Model Instance):
            The model we're getting the field type for
        attr_name (string):
            The name of the field we're checking if we don't already
            have the field
        field(Field object):
            If we already have the current field, it can be passed in. Else
            the method will try to get it by matching the attr_name
        raise_unfound(bool):
            If this is True, and the field is not found, 
            it will raise a FieldDoesNotExist exception
    """
    
    if not field:
        try:
            field = get_field_with_name(model_obj, attr_name)
        except models.FieldDoesNotExist:
            logger.info('Field %s on model %s not found.', attr_name, model_obj)
            if raise_unfound:
                raise 
            else:
                return False
    
    return isinstance(field, models.IntegerField) or\
           isinstance(field, models.DecimalField) or\
           isinstance(field, models.FloatField)

def get_field_with_name(model_info, field_name, case_insensitive=False):
    """
    Gets the Field object for the given field name of the given model
         
    RETURNS: 
        The current field object of the field we're attempting to set.
        If it cannot be found, returns None. Can also raise DoNotSetException
        and FieldDoesNotExist exception.
         
    PARAMS:
        model_info(Djnago Model):
            The Model instance that we're getting the field for
        field_name(string):
            The name of the field
    """
    
    if not case_insensitive:
        try:
            # Use Django Model Introspection to get the current Field instance
            # Field instance is first in the returned tuple
            field = model_info._meta.get_field_by_name(field_name)[0]
                
            if field.primary_key: 
                #NEVER allow setting primary key
                raise DoNotSetException("Cannot Set Primary Key!")
            
            return field
            
        except models.FieldDoesNotExist:
            raise
    
    else:
        
        for field in model_info._meta.fields:
            
            if field.name.lower() != field_name.lower():
                continue
            
            if field.primary_key: #NEVER allow setting the primary key, you nut!
                raise DoNotSetException("Cannot Set Primary Key!")
            
            return field
        
        raise models.FieldDoesNotExist("Field %s for model %s was not found", 
                                       field_name, 
                                       model_info)
    return None
            
            
def _field_null_and_default(field, value):
    """
    Checks to see if we should not set the field, depending on the fields nullable and
    default values. If the field should not be set, this will raise a DoNotSetException.
    
    RETURNS:
        Void
        
    PARAMS:
        field(Model Field class):
            The field we're checking the default values for
        value (any type):
            The value we're trying to check against to see if 
            we should just use the default values.
    """
    if not value:
        # If a null field comes in, but we don't allow for nulls, and we DO have a
        # default value, then do not set this field - it will take a default
        if not field.null and field.default is not models.NOT_PROVIDED:
            raise DoNotSetException("Null value on non-null field w/default value")

def _check_update_fk(**kwargs):
    """
    Checks to see if there is a flag in kwargs that does not allow setting foreign keys.
    If there is, a DoNotSetException is raised.
    """
    if kwargs.get('disallow_fk_update', False):
        raise DoNotSetException("Setting Foreign Keys is not allowed in this import")
    
def _transform_value_for_field(field, model_obj, value_to_transform, **kwargs):
    """
    Takes a value from salesforce, along with a model's field information and transforms
    the value from the field to make it work with our current field types
         
    RETURNS: 
        The transformed value from salesforce
         
    PARAMS:

        field(Django Field Instance):
            The instance of the Django Field that we're setting
        model_obj(Model Instance):
            The model we're attempting to update
        value_to_transform(any type):
            The value that is getting transformed to get stored in a Django model
        model_id(ID of the model we're trying to update/import)
            The ID of the model - used to create error messages
    """
        
    # Depending on field type, transform the value if necessary
    if isinstance(field, models.TextField):
            
        if value_to_transform is None:
            value_to_transform = ''
                
    elif isinstance(field, models.CharField):
            
        if value_to_transform is None:
            value_to_transform = ''
            
    elif isinstance(field, models.IPAddressField):
            
        if value_to_transform is None:
            value_to_transform = ''
            
    elif isinstance(field, models.FilePathField):
            
        if value_to_transform is None:
            value_to_transform = ''
            
    elif isinstance(field, models.IntegerField):
            
        if value_to_transform == '':
            value_to_transform = None
                
        _field_null_and_default(field, value_to_transform)
            
        if isinstance(value_to_transform, basestring):
            value_to_transform = int(Decimal(value_to_transform))
        
    elif isinstance(field, models.DateTimeField):

        if value_to_transform == '':
            value_to_transform = None
                            
        _field_null_and_default(field, value_to_transform)

        if isinstance(value_to_transform, basestring):
            
            datetime_format = "%Y-%m-%dT%H:%M:%S"
            datetime_format = kwargs.get('date_time_formatter', datetime_format)
            datetime_format = kwargs.get(field.attname + '_date_time_formatter', 
                                         datetime_format)
            
            value_to_transform = datetime.datetime.strptime(value_to_transform [:19], 
                                                            datetime_format)
                
    elif isinstance(field, models.DateField):
            
        if value_to_transform == '':
            value_to_transform = None
                
        _field_null_and_default(field, value_to_transform)
                
        if isinstance(value_to_transform, basestring):
            
            date_format = "%Y-%m-%d"
            date_format = kwargs.get('date_formatter', date_format)
            date_format = kwargs.get(field.attname + '_date_formatter', date_format)
                
            value_to_transform = datetime.datetime.strptime(value_to_transform[:10], date_format)
        
    elif isinstance(field, models.TimeField):
            
        if value_to_transform == '':
            value_to_transform = None
                
        _field_null_and_default(field, value_to_transform)
                
        if isinstance(value_to_transform, basestring):
            
            time_format = "%H:%M:%S"
            time_format = kwargs.get('time_formatter', time_format)
            time_format = kwargs.get(field.attname + '_time_formatter', time_format)
            
            value_to_transform = time.strptime(value_to_transform[:10], time_format)
            
    elif isinstance(field, models.DecimalField) or \
         isinstance(field, models.FloatField):
    
        if value_to_transform == '':
            value_to_transform = None
                        
        _field_null_and_default(field, value_to_transform)

        if isinstance(value_to_transform, basestring):
            value_to_transform = Decimal(value_to_transform)
                        
    elif isinstance(field, models.BooleanField) or\
         isinstance(field, models.NullBooleanField):
            
        if value_to_transform == '':
            value_to_transform = None
                
        _field_null_and_default(field, value_to_transform)
        
        if isinstance(value_to_transform, basestring):
            value_to_transform = value_to_transform.lower() == 'true' or\
                                 value_to_transform.lower() == '1' or\
                                 value_to_transform.lower() == 'yes' or\
                                 value_to_transform.lower() == 't' or\
                                 value_to_transform.lower() == 'y'
                
    elif isinstance(field, models.ForeignKey):
            
        _check_update_fk(**kwargs)
        
        value_to_transform = _tranform_foreign_key(value_to_transform, field, model_obj, **kwargs)
        
    elif isinstance(field, models.ManyToManyField):
            
        _check_update_fk(**kwargs)
        
        if isinstance(value_to_transform, basestring):
            value_to_transform = _tranform_foreign_key(value_to_transform.split(','), 
                                                            field, 
                                                            model_obj,
                                                            **kwargs)
            
            
    return value_to_transform

def _tranform_foreign_key(value_to_transform, field, model_obj, **kwargs):
    """
    Transforms the value for a foreign key to something that can be set on the object.
    Attempts to see if the object was already created. If not, attempts to get the object
    from the database.
         
    RETURNS: 
        The created foreign key object if found, else None if not found
         
    PARAMS:
        value_to_transform(string):
            The id of the object we're trying to transform into an FK reference
        field(Field object):
            The Django model field object for the foreign key field we're setting
        model_obj(Model Instance):
            The model we're updating
    """
    if value_to_transform:
            
        lookup_field = 'id'
        if field.attname + '_lookup_field' in kwargs:
            lookup_field = kwargs[field.attname + '_lookup_field']
            
        # Get related model information            
        related_model = field.rel.to
        class_name = related_model.__name__
            
        logger.debug("Trying to get foreign key reference from model %s field %s "
                     "with value %s for field %s on model %s",
                     model_obj, field.attname, value_to_transform, 
                     lookup_field, class_name)
                        
        logger.debug("Foreign key not created, attempting lookup")
                    
        if type(value_to_transform) == list: # M2M
            all_objs = []
            
            for val in value_to_transform:
                
                try:
                    related_obj = related_model.objects.get(**{lookup_field:val})
                    all_objs.append(related_obj)
                    
                except models.ObjectDoesNotExist:
            
                    try:
                        _fk_missing_fail(value_to_transform, 
                                         "Too many objects matched", 
                                         False, 
                                         **kwargs)
                    except DoNotSetException:
                        pass
            
                except MultipleObjectsReturned:
                    try:
            
                        _fk_missing_fail(value_to_transform, 
                                         "Too many objects matched", 
                                         False, 
                                         **kwargs)
                    except DoNotSetException:
                        pass
                        
            logger.debug("All M2M FK Relationships found. Returning list of relationships")
            return all_objs
        
        else: # Regular FK or 1To1
                
            try:
                related_obj = related_model.objects.get(**{lookup_field:value_to_transform})
                logger.debug("Foreign key found in database, returning object")
                return related_obj
                    
            except models.ObjectDoesNotExist:
                
                try:
                    _fk_missing_fail(value_to_transform, "Too many objects matched", True, **kwargs)
                except DoNotSetException:
                    pass
                
            except MultipleObjectsReturned:
                
                try:
                    _fk_missing_fail(value_to_transform, "Too many objects matched", True, **kwargs)
                except DoNotSetException:
                    pass
    else:
            
        # If there is a null reference, and we don't allow for nulls to a foreignkey field
        # we must raise a failing error for this outbound message
        if not field.null and field.default is models.NOT_PROVIDED:
            
            logger.exception("Foreign Key cannot be resolved. "
                             "Null value given for a field that cannot be null.")
            raise ImportFKMissingException()
        else:
            # if there is no data and it's nullable just don't set it
            raise DoNotSetException("Null value on null field w/default null value")
                
def _fk_missing_fail(field, value_to_transform, msg, check_null, **kwargs):
    """
    Determines if setting an FK should fail
    
    RETURNS:
        Void
    
    PARAMS:
        field (Field object):
            The field info of the field we're attempting to set
        value_to_transform (any type):
            The value we're using to query
    """
    # If there is a null reference, and we don't allow for nulls to a foreignkey field
    # we must raise a failing error for this outbound message
    if check_null and not field.null and field.default is models.NOT_PROVIDED:
                
        logger.exception("Foreign Key cannot be resolved. "
                         "Null value given for a field that cannot be null.")
        raise ImportFKMissingException()
                
    else:
        fail_attr = kwargs.get(field.attname + '_fail_missing_fk', False)
        fail_all = kwargs.get('fail_missing_fk', False)
                    
        if fail_attr or fail_all:
            logger.exception("Foreign Key cannot be resolved. %s", msg)
            raise ImportFKMissingException()
        else:
            logger.warning("Foreign Key cannot be resolved. %s. Skipping Setting this value.", msg)
            raise DoNotSetException()
    
class DoNotSetException(Exception):
    pass

class ImportFKMissingException(Exception):
    pass
