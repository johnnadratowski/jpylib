#!/usr/bin/env python
"""
Contains a class that can update a machines hosts file.
"""
import datetime
import logging
import optparse
import traceback
import sys

from .base import AmazonBase


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class AmazonUpdateHosts(AmazonBase):
    """
    Class that can update a local hosts file to point to the resources
    that we get from Amazon AWS
    """

    TAG_HOSTNAME = 'Name'

    HOSTS_FILE_PATH = '/etc/hosts'

    BEGIN_STRING = '# BEGIN AMAZON HOSTS ENTRIES'
    END_STRING = '# END AMAZON HOSTS ENTRIES'

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

        parser.add_option("-f", "--hosts_file", dest="hosts_file",
                             help="The file path to the hosts file we want to change.",
                             default=cls.HOSTS_FILE_PATH)

        parser.add_option("-d", "--backup_date",
                             action="store_true", dest="backup_date", default=False,
                             help="If true, the current date will be appended on the backup file name.")

        parser.add_option("-e", "--external_ip",
                             action="store_true", dest="external_ip", default=False,
                             help="If true, the external IP will be used for the hosts file.")

        parser.add_option("-t", "--tag_hostname", dest="tag_hostname",
                             help="The tag we want to use to get the host name.",
                             default=cls.TAG_HOSTNAME)

        return parser

    def __init__(self, logger=logger, **options):

        super(AmazonUpdateHosts, self) .__init__(logger=logger, **options)

    def _get_host_lines(self):

        new_lines = [self.BEGIN_STRING + '\n']

        for reservation in self.reservations:
            for inst in reservation.instances:

                ip = inst.ip_address if self._external_ip else inst.private_ip_address
                if not hasattr(inst, 'tags') or not inst.tags:
                    continue

                alias_name = inst.tags.get(self._tag_hostname, '').strip()

                if alias_name and ' ' in alias_name:
                    # replace spaces with hyphens
                    alias_name = alias_name.replace(' ', '-')

                new_line = '{ip} {dns_name} {alias}\n'
                new_line = new_line.format(ip=ip,
                                           dns_name=inst.dns_name,
                                           alias=alias_name)

                new_lines.append(new_line)

        new_lines.append(self.END_STRING)
        new_lines.append('\n')

        return new_lines

    def _get_hosts_file(self, mode='r'):

        try:
            hosts_file = file(self._hosts_file, mode)
        except IOError:
            # No File
            return []
        except:
            self.logger.exception("An exception occurred trying to open hosts file.")
            sys.exit()

        if mode == 'r':
            lines = hosts_file.readlines()

            if not self._no_backup:
                back_path = self._backup_file
                if not back_path:
                    back_path = self._hosts_file + ".bak"

                if self._backup_date:
                    back_path += '.{date}'.format(date=datetime.date.today().strftime('%d-%m-%y'))

                try:
                    bak_file = file(back_path, 'w')
                    bak_file.writelines(lines)
                    bak_file.close()
                except:
                    ans = raw_input(
                        "Could not save backup file of hosts to "
                        "{back_path}. Exception: {exc}. \n\nContinue "
                        "with script run? [N/y]:  ".format(exc=traceback.format_exc(),
                                                           back_path=back_path)
                    )

                    if not ans.strip() or ans.strip().lower().startswith('n'):
                        self.logger.info("Exiting script because of user input.")
                        sys.exit()

            return lines

        else:
            return hosts_file

    def write_host_file(self):

        lines = self._get_hosts_file()

        try:
            index_begin = lines.index(self.BEGIN_STRING + '\n')
            index_end = lines.index(self.END_STRING + '\n')
        except:
            index_begin = None
            index_end = None

        new_lines = self._get_host_lines()

        if lines:
            if index_begin and index_end:
                logger.info("ORIGINAL: \n\n" + "".join(lines[index_begin:index_end + 1]))
            else:
                logger.info("ORIGINAL: \n\n" + "".join(lines))
            logger.info("\n#--------------------------------------------------------------------#")
            logger.info("#--------------------------------------------------------------------#")
            logger.info("#--------------------------------------------------------------------#\n\n")

        logger.info("NEW: \n\n" + "".join(new_lines))

        ans = raw_input("Replace original entries with new ones? [Y/n]").lower().strip()
        if ans and ans.startswith('n'):
            logger.info("Not writing file at user request. Exiting.")
            sys.exit()

        if index_begin is not None:
            begin_new_lines = lines[0:index_begin]
            end_new_lines = lines[index_end + 1:]
            all_lines = begin_new_lines + new_lines + end_new_lines
        elif not lines:
            all_lines = new_lines
        else:
            begin_index = None
            for idx, line in enumerate(lines):
                if not line.strip():
                    begin_index = idx
                    break

            if begin_index is None:
                all_lines = lines + new_lines
            else:
                begin_new_lines = lines[0:begin_index]
                end_new_lines = lines[begin_index + 1:]
                all_lines = begin_new_lines + new_lines + end_new_lines

        hosts_file = self._get_hosts_file('w')

        hosts_file.writelines(all_lines)

        hosts_file.close()

        self.logger.info('Hosts file is successfully written')


def run_host_update(*args, **options):

    try:
        obj = AmazonUpdateHosts(**options.__dict__)
        obj.write_host_file()
    except SystemExit:
        pass
    except:
        print "An exception occurred trying to write hosts file. "
        traceback.print_exc()

if __name__ == '__main__':
    (options, args) = AmazonUpdateHosts.get_optparser().parse_args()
    run_host_update(*args, **options)

