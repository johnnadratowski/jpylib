"""
Contains base classes for working with Amazon AWS
"""
import logging
from optparse import OptionParser

import boto


logger = logging.getLogger(__name__)

class AmazonBase(object):
    """
    Base object for creating a service to communicate with Amazon
    """

    AWS_ACCESS_KEY='access_key'
    AWS_SECRET_KEY='secret_key'

    OPTPARSER = OptionParser(add_help_option=False)

    OPTPARSER.add_option("-a", "--access_key", dest="access_key",
                         help="The access key to use to connect to the Amazon AWS API",
                         default=AWS_ACCESS_KEY)

    OPTPARSER.add_option("-s", "--secret_key", dest="secret_key",
                         help="The secret key to use to connect to the Amazon AWS API",
                         default=AWS_SECRET_KEY)

    def __init__(self, logger=logger, **options):

        self._connection = None
        self.logger = logger

        for k,v in options.iteritems():
            setattr(self, "_" + k, v)

        if not hasattr(self, '_access_key'):
            self._access_key = self.AWS_ACCESS_KEY

        if not hasattr(self, '_secret_key'):
            self._secret_key = self.AWS_SECRET_KEY
        self._options = options

    @property
    def connection(self):
        if self._connection is None:
            self._connection = boto.connect_ec2(self._access_key, self._secret_key)
        return self._connection

    @property
    def reservations(self):
        return self.connection.get_all_instances()

