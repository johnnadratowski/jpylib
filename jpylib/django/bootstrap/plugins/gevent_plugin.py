"""
Bootstrap plugin for gevent
"""
import os
from gevent import monkey


if int(os.environ.get('ENABLE_GEVENT', '0')):
    # Don't monkey patch if disable gevent is set on environment.
    monkey.patch_all()

