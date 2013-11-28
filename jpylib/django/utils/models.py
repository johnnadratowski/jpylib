"""
Contains helper methods for working with Django models.
"""
from jpylib.functional import item_split, filter_all


def split_field_list(fields):
    """
    Used to split model field arguments, using the
    "__" convention in django model field queries.
    :param fields: The list of arguments to split
    :return:
    """
    if not fields:
        return None, None

    output = item_split(lambda x: x.partition("__"), fields)

    output = filter_all(lambda x: x != "", output)

    return (output[0], output[2]) if output else (None, None)


def model_to_dict(instance,
                  fields=None,
                  exclude=None,
                  only_editable=False,
                  follow_fk=None):
    """
    Returns a dict containing the data in ``instance``
    suitable for passing as a Form's ``initial`` keyword argument.
    For fields and follow_fk, allows '__' separator in the names
    to specify fields on related models.

    :param fields: An optional list of field names.  If provided,
                   only the named fields will be included
                   in the returned dict.

    :param exclude: An optional list of field names. If provided,
                    the named fields will be excluded from the
                    returned dict, even if they are listed in
                    the ``fields`` argument.

    :param only_editable: If true, do not return fields
                          that have editable=False

    :param follow_fk: Specifies when to follow foreign key fields to
                      allow for retrieving related data
    """
    fields_curr, fields_next = split_field_list(fields)
    exclude_curr, exclude_next = split_field_list(exclude)
    fk_curr, fk_next = split_field_list(follow_fk)

    opts = instance._meta

    data = {}
    for f in opts.fields + opts.many_to_many:
        if only_editable and not f.editable:
            continue
        if fields_curr and not f.name in fields_curr:
            continue
        if exclude_curr and f.name in exclude_curr:
            continue
        if isinstance(f, ManyToManyField):
            # If the object doesn't have a primary key yet, just use an empty
            # list for its m2m fields. Calling f.value_from_object will raise
            # an exception.
            if instance.pk is None:
                data[f.name] = []
            elif fk_curr and f.name in fk_curr:
                data[f.name] = [
                    model_to_dict(obj,
                                  fields=fields_next,
                                  exclude=exclude_next,
                                  only_editable=only_editable,
                                  follow_fk=fk_next)
                    for obj in f.value_from_object(instance)]
            else:
                data[f.name] = [
                    obj.pk for obj in f.value_from_object(instance)
                ]
        if isinstance(f, ForeignKey) and fk_curr and f.name in fk_curr:
            data[f.name] = model_to_dict(getattr(instance, f.name),
                                         fields=fields_next,
                                         exclude=exclude_next,
                                         only_editable=only_editable,
                                         follow_fk=fk_next)

        else:
            data[f.name] = f.value_from_object(instance)
    return data

