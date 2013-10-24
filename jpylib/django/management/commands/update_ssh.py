"""
Management command to update the hosts file from Amazon
"""
from django.core.management.base import BaseCommand, CommandError

from .amazon import AmazonUpdateSSH, run_ssh_update

class Command(BaseCommand):
    """
    Management command to update the hosts file from Amazon
    """

    option_list = (BaseCommand.option_list +
                   tuple(AmazonUpdateSSH.get_optparser(add_help=False).option_list))

    help = 'Updates the local SSH config to add new amazon box entries'

    def handle(self, *args, **options):
        try:
            run_ssh_update(*args, **options)
        except Exception, ex:
            raise CommandError("Exception occurred during ssh config update.", ex)

