"""
Plugin to bootstrap MongoEngine if there is a
MONGO_DATABASES setting available.  Should be in the same format
as the Django DATABASES, with the keys being the db name and
the values being passed to connect as kwargs.  If using more than
one DB, ensure that the alias is set in the values.
"""

from django.conf import settings


dbs = getattr(settings, 'MONGO_DATABASES', None)
if dbs:
    # If there are dbs set up in MONGO_DATABASES in the settings,
    # initialize the connections to them so this won't need to
    # be done manually later.
    from mongoengine import connect
    for db, kwargs in dbs.iteritems():
        connect(db, **kwargs)

else:
    print "No MONGO_DATABASES setting found.  Mongo is not instantiated!"
