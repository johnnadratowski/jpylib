#!/usr/bin/env python
"""
Contains a class that can update a machines ssh file.
"""
import datetime
import logging
import optparse
import os
import sys
import traceback

from .base import AmazonBase


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

class AmazonUpdateSSH(AmazonBase):
    """
    Class that can update a users .ssh config so that they can automatically
    ssh into an Amazon machine.
    """

    TAG_HOSTNAME = 'Name'

    FORMAT_STRING = """\nHost {alias_name}\n\tUser ubuntu\n\tHostName {alias_name}\n\tIdentityFile {pem_file}\n\n"""

    @classmethod
    def get_optparser(cls, add_help=True):

        parser = optparse.OptionParser(option_list=AmazonBase.OPTPARSER.option_list,
                                       add_help_option=add_help)

        parser.add_option("-b", "--backup_file", dest="backup_file",
                             help="The file path to which we want to backup the file.",
                             default='')

        parser.add_option("-B", "--no_backup",
                             action="store_true", dest="no_backup", default=False,
                             help="If true, no backup file will be created")

        parser.add_option("-f", "--ssh_file", dest="ssh_file",
                             help="The file path to the ssh file we want to change.",
                             default=None)

        parser.add_option("-p", "--pem_file", dest="pem_file",
                             help="The file path to the pem file.",
                             default=None)

        parser.add_option("-d", "--backup_date",
                             action="store_true", dest="backup_date", default=False,
                             help="If true, the current date will be appended on the backup file name.")

        parser.add_option("-t", "--tag_hostname", dest="tag_hostname",
                             help="The tag we want to use to get the host name.",
                             default=cls.TAG_HOSTNAME)

        return parser

    def __init__(self, logger=logger, **options):

        super(AmazonUpdateSSH, self).__init__(logger=logger, **options)

        if getattr(self, '_ssh_file', None) is None:
            logger.error("No ssh file specified. Cannot update SSH file. Exiting")
            sys.exit()

        if getattr(self, '_pem_file', None) is None:
            logger.error("No pem file specified. Cannot update SSH file. Exiting")
            sys.exit()

    def _get_ssh_lines(self, lines):

        new_lines = []

        for reservation in self.reservations:
            for inst in reservation.instances:

                alias_name = inst.tags.get(self._tag_hostname, '').strip()
                if not hasattr(inst, 'tags') or not inst.tags:
                    continue

                if alias_name and ' ' in alias_name:
                    # replace spaces with hyphens
                    alias_name = alias_name.replace(' ', '-')

                if not alias_name:
                    continue

                cont = False
                for line in lines:
                    if alias_name in line:
                        cont = True
                        break
                if cont:
                    continue

                new_line = self.FORMAT_STRING
                new_line = new_line.format(alias_name=alias_name,
                                           pem_file=self._pem_file)

                if new_line:
                    new_lines.append(new_line)

        return new_lines

    def _get_ssh_file(self, mode='r'):

        if mode == 'r' and not os.path.exists(self._ssh_file):
            self.logger.warn("SSH config file does not yet exist, returning empty string for lines")
            return []

        try:
            ssh_file = file(self._ssh_file, mode)
        except:
            self.logger.exception("An exception occurred trying to open ssh file. Exiting.")
            sys.exit()

        if mode == 'r':
            lines = ssh_file.readlines()

            if not self._no_backup:
                back_path = self._backup_file
                if not back_path:
                    back_path = self._ssh_file + ".bak"

                if self._backup_date:
                    back_path += '.{date}'.format(date=datetime.date.today().strftime('%d-%m-%y'))

                try:
                    bak_file = file(back_path, 'w')
                    bak_file.writelines(lines)
                    bak_file.close()
                except:
                    ans = raw_input(
                        "Could not save backup ssh file to "
                        "{back_path}. Exception: {exc}. \n\nContinue "
                        "with script run? [Y/n]:  ".format(exc=traceback.print_exc(),
                                                           back_path=back_path)
                    )

                    if not ans.strip() or ans.strip().lower().startswith('n'):
                        self.logger.info("Exiting script because of user input.")
                        sys.exit()

            return lines

        else:
            return ssh_file

    def write_ssh_file(self):
        """
        Writes the .ssh config file out to the file system
        """

        lines = self._get_ssh_file()

        new_lines = self._get_ssh_lines(lines)

        ssh_file = self._get_ssh_file(mode='w')

        ssh_file.writelines(lines + new_lines)

        ssh_file.close()

        print 'SSH config file is successfully written'

def run_ssh_update(*args, **options):
    try:
        obj = AmazonUpdateSSH(**options.__dict__)
        obj.write_ssh_file()
    except SystemExit:
        pass
    except:
        print "An exception occurred trying to write hosts file."
        traceback.print_exc()

if __name__ == '__main__':
    (options, args) = AmazonUpdateSSH.get_optparser().parse_args()
    run_ssh_update(*args, **options)

