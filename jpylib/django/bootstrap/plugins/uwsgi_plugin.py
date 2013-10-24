"""
Contains bootstrap plugins for uWSGI integration
"""
from django.utils import autoreload

from django.conf import settings


try:
    import uwsgi
    from uwsgidecorators import timer

    @timer(3)
    def change_code_graceful_reload(sig):
        """
        This method allows for the django runserver's autoreload
        capability in uWSGI.
        """
        if (getattr(settings, 'DEBUG', False)
            and getattr(settings, 'UWSGI_AUTORELOAD', False)
            and autoreload.code_changed()):

            uwsgi.reload()

except ImportError:
    print "uWSGI not being used.  Cannot load uWSGI plugin"

