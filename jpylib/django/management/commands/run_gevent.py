#!/usr/bin/env python
"""
This is the script that will start up the Gevent WSGI server
"""
import multiprocessing
import optparse

from gevent import monkey
from gevent.os import fork

from django.core.management.base import BaseCommand, CommandError

from .django import bootstrap


class Command(BaseCommand):
    """
    Management command to run non-blocking gevent WSGI server
    """

    option_list = BaseCommand.option_list
    option_list += (
        optparse.make_option('-w', '--child-workers', dest='child_workers',
                             help='The number of CHILD workers to spawn. '
                                  'Set to 0 for 1 worker',
                             default=multiprocessing.cpu_count()),
        optparse.make_option('-s', '--disable-socketio', dest='disable_socketio',
                             action='store_true',
                             help='Set if you want to disable socketio support',
                             default=False),
        optparse.make_option('-p', '--disable-psycogreen', dest='disable_psycogreen',
                             action='store_true',
                             help='Set if you want to disable psycogreen support',
                             default=False),
    )

    help = ('Runs non-blocking Gevent WSGI server with '
            'psycogreen. Defaults to listening on 0.0.0.0:80')

    args = '[optional port number, or ipaddr:port]'

    def handle(self, *args, **options):
        try:
            host = port = None

            if len(args) > 0:
                host = args[0]
                if ':' in host:
                    host, port = host.rsplit(':')

            if host is None:
                host = '0.0.0.0'
            if port is None:
                port = 80

            # Monkey Patch for Gevent
            monkey.patch_all()

            if not options['disable_psycogreen']:
                # Monkey Patch for Psycopg2 using psycogreen
                import psycogreen.gevent
                psycogreen.gevent.patch_psycopg()

            application = bootstrap.get_wsgi_application()

            if options['disable_socketio']:
                from gevent.pywsgi import WSGIServer
                server = WSGIServer((host, int(port)), application)
            else:
                from socketio.server import SocketIOServer
                server = SocketIOServer((host, int(port)), application, resource="socket.io")

            print 'Starting server on {host}:{port} with {workers} workers.'.format(
                host=host,
                port=port,
                workers=options['child_workers']
            )

            server.start()

            print 'Listening on http://{host}:{port}'.format(host=host, port=port)

            for i in range(options['child_workers']):
                pid = fork()
                if pid == 0:
                    break

            server.serve_forever()

        except Exception, ex:
            raise CommandError("Exception occurred during gevent wsgi process startup.", ex)

