#!/usr/bin/env python
"""
Management command to generate sphinx documentation
"""
import optparse
import os
from os.path import abspath, dirname, join, expanduser
import sys
import subprocess
import time

from watchdog.events import FileSystemEventHandler

from django.core.management.base import BaseCommand, CommandError


class CompileEventHandler(FileSystemEventHandler):
    """
    Event handler for watchdog file system event alerts.
    """

    def __init__(self, sphinx_compiler):
        self._sphinx_compiler = sphinx_compiler

    def on_any_event(self, event):
        """
        This will fire when any file system event occurs in the current path
        """
        if ('_compile' not in event.src_path and
                not event.src_path.startswith(self._sphinx_compiler.project_rst_path) and
                not event.src_path.startswith(self._sphinx_compiler.app_rst_path) and
                event.src_path.endswith('.rst')):

            print "Change in file @ {} detected. Recompiling.".format(event.src_path)
            self._sphinx_compiler._compile_all()
            print "Compilation process complete.  Here, have a cookie."
            print "Watching folder @ {} for changes.".format(self._sphinx_compiler.doc_path)


class Command(BaseCommand):
    """
    Class that can automatically generate sphinx output.
    """

    option_list = BaseCommand.option_list
    option_list += (
        optparse.make_option('-w', '--watch', action='store_true', dest='watch', default=False,
                             help="Set to watch file system documentation directory"
                                  "and recompile when changes occur."),
        optparse.make_option('-c', '--clean', dest='clean', action='store_true', default=False,
                             help="Set to clean the old compiled output before compiling"),
        optparse.make_option('-i', '--interactive', dest='interactive',
                             action='store_true', default=False,
                             help="Runs the documentation generator in interactive mode"),
        optparse.make_option('-a', '--autodoc', dest='autodoc', action='store_true', default=False,
                             help="Set to have the documentation generator run autodoc"),
        optparse.make_option('-f', '--force', dest='force', action='store_true', default=False,
                            help="Will forcefully overwrite the sphinx-apidoc generated rst files"),
        optparse.make_option('-o', '--output-type', dest='output_type', default='html',
                            help="The type of output to make from sphinx. Defaults to html."),
    )

    args = ['Path to project docs folder. Defaults to current directory.']

    help = "Runs the documentation generator."

    def handle(self, *args, **options):
        """
        Handles management command

        :param args: arguments to command
        :type args: list
        :param options: options to command
        :type params: optparse options
        """
        try:
            self.options = options

            self.doc_path = abspath(args[0] if args else '.')

            self.project_root = abspath(dirname(self.doc_path))

            self.project_path = join(self.project_root, 'project')
            self.project_rst_path = join(self.doc_path, 'root')

            self.app_path = join(self.project_root, 'apps')
            self.app_rst_path = join(self.doc_path, 'apps')

            self.project_path = os.environ.get('PROJECT_PYTHON_STDLIB',
                                                   expanduser('~/git/jpylib'))
            self.project_rst_path = join(self.doc_path, 'project')

            os.environ['PYTHONPATH'] += os.pathsep.join(sys.path)
            os.environ['ENABLE_GEVENT'] = '0'

            self.compile()

        except Exception, ex:
            raise CommandError("Exception occurred during sphinx document generation", ex)

    def compile(self):
        """
        Generate autodoc rst files from code docstrings and compile sphinx output
        """
        if self.options.get('watch', False):
            # If the watch folder is set, we will set up
            # an observer using watchdog and re-compile on code change

            from watchdog.observers import Observer

            observer = Observer()
            handler = CompileEventHandler(self)
            observer.schedule(handler, path=self.doc_path, recursive=True)
            observer.start()

            print "Watching folder @ {} for changes.".format(self.doc_path)

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print "Stopping watch folder and Exiting."
                observer.stop()
            observer.join()

            print "Goodbye"

        else:

            print "Compiling autodoc rst and sphinx files"

            self._compile_all()

            print "Files compiled. Goodbye"

    def _compile_all(self):
        """
        Compiles all of the rst files and sphinx documents
        """
        if self.options['clean']:
            self._clean()

        if self.options['autodoc']:
            self._autodoc()

        self._compile()

    def _clean(self):
        """
        Clean the old output
        """
        subprocess.call('make clean', shell=True, env=os.environ)

    def _compile(self):
        """
        Compile the sphinx documents to the output type specified
        """
        # Ensure we run the make call in the proper directory.
        # return to original directory afterwards
        orig_dir = os.curdir
        os.chdir(self.doc_path)
        subprocess.call(
            ' '.join(['make', self.options['output_type']]),
            shell=True,
            env=os.environ
        )
        os.chdir(orig_dir)

    def _autodoc(self):
        """
        Run the autodoc on the modules to generate the rst files from docstrings
        """
        if self.options['interactive']:
            raw_input(
                "Outputting RST files to {app} for "
                "apps and {project} for project stdlib. "
                "(Press ENTER to continue or CTRL-C to exit)".format(app=self.app_rst_path,
                                                                     project=self.project_rst_path)
            )

        subprocess.call(
            ' '.join([
                'sphinx-apidoc',
                '-f' if self.options.get('force', False) else '',
                '-o',
                self.app_rst_path,
                self.app_path
            ]),
            shell=True,
            env=os.environ
        )

        subprocess.call(
            ' '.join([
                'sphinx-apidoc',
                '-f' if self.options.get('force', False) else '',
                '-o',
                self.project_rst_path,
                self.project_path
            ]),
            shell=True,
            env=os.environ
        )

        subprocess.call(
            ' '.join([
                'sphinx-apidoc',
                '-f' if self.options.get('force', False) else '',
                '-o',
                self.project_rst_path,
                self.project_path
            ]),
            shell=True,
            env=os.environ
        )
