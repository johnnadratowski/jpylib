"""
Contains utilities used when booting up Django.  bootstrap() method
should be called when application boots up.  App-level folders will
have their bootstrap python modules/packages loaded.  Environment
variables and PYTHONPATH are set up. Other misc services are initialized.
"""
import os

from django.core.wsgi import get_wsgi_application
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

from .exceptions import *
from .path import *
from . import plugins


def define_settings_module_env(settings_namespace=None, env_var=None):
    """
    Sets the DJANGO_SETTINGS_MODULE to the environment variable value if specified,
    else it will set it to the given namespace if specified.

    :param settings_namespace: The namespace of the settings file to set to DJANGO_SETTINGS_MODULE
    :type settings_namespace: string
    :param env_var: environment variable to check for the settings namespace
    :type env_var: string
    :raises: BootstrapException
    :returns: the string to the namespace of the settings package
    """

    if env_var and os.environ.get(env_var):
        settings_namespace = os.environ[env_var]
    elif env_var and settings_namespace:
        os.environ[env_var] = settings_namespace

    if not settings_namespace:
        raise BootstrapException(
            "Could not get the settings module namespace.  Please either specify "
            "the settings_namespace manually, or set the {env_var} "
            "in your environment variables.".format(env_var=env_var)
        )

    os.environ["DJANGO_SETTINGS_MODULE"] = settings_namespace

    return settings_namespace


def bootstrap_wsgi():
    """
    Used to get and bootstrap the Django WSGI application
    """
    return get_wsgi_application()


def import_submodule(module, package, submodule):
    """
    This code was taken from the Pinax project.  It is used
    to load a submodule from a package

    :param module: The package loaded module
    :type module: python module
    :param app: the app we're loading the submodule from
    :type app: string
    :param submodule: the submodule we're loading form the app
    :type sudmodule: string
    """
    # noinspection PyBroadException
    try:
        import_module("{}.{}".format(package, submodule))
    except:
        if module_has_submodule(module, submodule):
            raise


def load_app_modules(apps, submodules):
    """
    This code was taken from the Pinax project.  It will initialize
    submodules for all the installed apps if they match the given
    strings in the submodules list.

    :param apps: List of apps to load the submodules from
    :type apps: list of strings representing django apps
    :param submodules: List of submodules from :setting:`INSTALLED_APPS` to load
    :type submodules: list of strings representing app modules
    """
    for app in apps:
        mod = import_module(app)
        for submodule in submodules:
            import_submodule(mod, app, submodule)


def load_plugins(plugin_list):
    """
    Loads the given plugins from the plugins folder.  Ensure this
    is called after we can load the settings.  Essentially,
    DJANGO_SETTINGS_MODULE needs to be set.

    :param plugin_list: List of plugins to load
    :type plugin_list: list of strings
    """
    for plugin in plugin_list:
        import_submodule(plugins, 'project.django.bootstrap.plugins', plugin)

