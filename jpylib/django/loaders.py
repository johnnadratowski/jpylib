"""
Template loader for compiling .jade and .styl files
"""
import logging
import hashlib
import os
from subprocess import check_output, PIPE, CalledProcessError

from django.conf import settings

from pyjade.ext.django.loader import Loader as PyJadeLoader


logger = logging.getLogger(__name__)

class JadeStylusLoader(PyJadeLoader):

    def load_template(self, template_name, template_dirs=None):
        key = template_name
        if template_dirs:
            # If template directories were specified, use a hash to differentiate
            key = '-'.join([template_name, hashlib.sha1('|'.join(template_dirs)).hexdigest()])

        if settings.DEBUG or key not in self.template_cache:

            if os.path.splitext(template_name)[1] in ('.styl',):

                source, display_name = self.load_template_source(template_name, template_dirs)

                # Just pipe the Stylus source directly to the stylus binary.
                command = """echo "{source}" | stylus -l""".format(source=source)
                try:
                    output = check_output(command, shell=True, stdin=PIPE, stderr=None)
                except CalledProcessError:
                    logger.exception('An exception occurred '
                                     'attempting to compile stylus file "%s". ',
                                     template_name)
                    return None, None

                self.template_cache[key] = output

            else:
                return super(Loader, self).load_template(template_name, template_dirs=template_dirs)

        return self.template_cache[key], None
