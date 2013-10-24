"""
Management command to update the hosts file from Amazon
"""
from django.core.management.base import BaseCommand, CommandError

from .amazon import AmazonUpdateHosts, run_host_update

class Command(BaseCommand):
    """
    Management command to update the hosts file from Amazon
    """

    option_list = (BaseCommand.option_list +
                   tuple(AmazonUpdateHosts.get_optparser(add_help=False).option_list))

    help = 'Updates the local hosts file to point to Amazon boxes'

    def handle(self, *args, **options):
        try:
            run_host_update(*args, **options)
        except Exception, ex:
            raise CommandError("Exception occurred during host update.", ex)

