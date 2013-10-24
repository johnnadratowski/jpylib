"""
This is used to bootstrap the psycogreen module
"""
import os
import psycogreen.gevent


if int(os.environ.get('ENABLE_GEVENT', '0')) and int(os.environ.get('ENABLE_PSYCOGREEN', '1')):

    # Disable psycogreen if gevent or psycogreen are disabled in environment
    psycogreen.gevent.patch_psycopg()
