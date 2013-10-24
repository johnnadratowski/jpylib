"""
Contains utilities used for bootstrapping the application's paths.
"""
import os
from os.path import abspath, dirname, join, isfile, isdir, expanduser
import sys

from .exceptions import BootstrapException


def process_path(path, env_var=None, add_path=False):
    """
    Processes a library path before returning to the caller. Will
    add to environment if env_var is specified and will add to path
    if add_path is True

    :param path: The path we're processing
    :type path: string to file system path
    :param env_var: The environment variable to set to the path, if specified
    :type env_var: string
    :param add_path: If true, this path will be added to sys.path
    :type add_path: boolean
    :raises: BootstrapException
    :returns: the path variable that was originally passed in, unmodified
    """

    if not isdir(path):
        raise BootstrapException(
            "The path {path} was given as a library path, but it does not exist "
            "in the file system.  Please check your paths and re-configure."
        )

    if env_var and os.environ.get(env_var) != path:
        # If this path has a corresponding environment variable, and
        # it isn't currently set properly in the environment, set it.
        os.environ[env_var] = path

    if add_path and not path in sys.path:
        # If add_path is true, and path not in sys.path, add this path to sys.path
        sys.path.insert(0, path)

    return path


def check_env_var(env_var, add_path=False):
    """
    Checks to see if the environment variable is set for a library path.
    If it is, it'll process it in :func:`process_path` and return the path
    set in the environment variable.  If not found, returns None.

    :param env_var: The environment variable to check for the library path
    :type env_var: string
    :param add_path: If true, this path will be added to sys.path
    :type add_path: boolean
    :returns: Path from environment variable env_var if found, else None
    """

    if env_var:
        path = os.environ.get(env_var)
        if path:
            # Expand user in case people put ~ in the environment variable
            path = expanduser(path)

            # If the project root path was already set in the environment variable,
            # use that as the project root path
            return process_path(path, env_var=env_var, add_path=add_path)


def clean_path(path):
    """
    Cleans the given path, ensuring it doesn't contain ~, ensuring it's
    absolute, and if it's a file, taking it's parent directory.

    :param path: Path we're cleaning.
    :type path: string to a file system path.
    :returns: The cleaned path.
    """

    # Ensure we're working with an absolute path that, and process home ~
    path = abspath(expanduser(path))

    if isfile(path):
        # If this is a file, get the directory parent
        path = dirname(path)

    return path


def get_project_root(path=None, env_var='DJANGO_PROJECT_ROOT', add_path=False):
    """
    Gets the project root folder by first checking an environment variable if
    specified.  If it doesn't exist in the environment variable, it attempts
    to traverse the tree up from the given path variable and find the folder
    containing the project's .git folder.

    :param path: The path we're attempting to traverse if there is no environment variable
    :type path: string to file system path
    :param env_var: The environment variable to check for the project root folder path
    :type env_var: string
    :param add_path: If true, this path will be added to sys.path
    :type add_path: boolean
    :raises: BootstrapException
    :returns: Project root path.
    """

    project_root = check_env_var(env_var, add_path=add_path)
    if project_root:
        return project_root

    if not path:
        # If there was no child path specified, we cannot get the project root
        raise BootstrapException(
            "Cannot get project root path unless environment variable {env_var} "
            "is set, or if a path to traverse the tree is given "
            "in the 'path' variable.".format(env_var=env_var)
        )

    path = clean_path(path)

    while project_root is None:
        # While we do not have the root path, traverse up the tree
        # to find the .git folder.
        if path == "/":
            raise BootstrapException(
                "Could not find project root looking for .git folder. "
                "It seems you might have customized things.  Please set {env_var} "
                "to the project's root path.".format(env_var=env_var)
            )

        if not isdir(join(path, '.git')):
            # If there is no .git folder here, we're not at the root yet.
            # Continue traversing up the directory structure
            path = abspath(join(path, ".."))
            continue

        project_root = path

    return process_path(project_root, env_var=env_var, add_path=add_path)


def get_git_root(project_root=None, env_var='DJANGO_GIT_ROOT', add_path=False):
    """
    Gets the git root folder by first checking an environment variable if
    specified.  If it doesn't exist in the environment variable, it assumes
    that the parent folder of the given project_root parameter is the git root.

    :param project_root: The path to the root of the project
    :type project_root: string to file system path of the project root
    :param env_var: The environment variable to check for the git root folder path
    :type env_var: string
    :param add_path: If true, this path will be added to sys.path
    :type add_path: boolean
    :raises: BootstrapException
    :returns: Git root path.
    """

    git_root = check_env_var(env_var, add_path=add_path)
    if git_root:
        return git_root

    if not project_root:
        # If there was no project path specified, we cannot get the git root
        raise BootstrapException(
            "Cannot get git root path unless environment variable {env_var} "
            "is set, or if a project root path to traverse the tree is given "
            "in the 'project_root' variable.".format(env_var=env_var)
        )

    project_root = clean_path(project_root)

    # If we're using the project root path, assume git root path is one
    # directory up from the project path
    git_root = abspath(join(project_root, '..'))

    return process_path(git_root, env_var=env_var, add_path=add_path)


def add_library_root(root=None, lib_folder=None, env_var=None, add_path=True):
    """
    Gets the specified library root folder by first checking an environment variable if
    specified.  If it doesn't exist in the environment variable, it just concatenates
    the root parameter and the lib_folder.

    :param root: The root path the library is nested underneath
    :type root: string to file system path
    :param lib_folder: The child path to root containing the library folder
    :type lib_folder: string to sub-path of root
    :param env_var: The environment variable to check for the library root folder path
    :type env_var: string
    :param add_path: If true, this path will be added to sys.path
    :type add_path: boolean
    :returns: Library folder path.
    """

    lib_root = check_env_var(env_var, add_path=add_path)
    if lib_root:
        return lib_root

    if not root or not lib_folder:
        # If there was no project path specified, we cannot get the git root
        raise BootstrapException(
            "Cannot get library root path unless environment variable {env_var} "
            "is set, or if a root path and library folder are specified.".format(env_var=env_var)
        )

    root = clean_path(root)

    # When adding a library, just join the library folder and the root path
    lib_root = abspath(join(root, lib_folder))

    return process_path(lib_root, env_var=env_var, add_path=add_path)



