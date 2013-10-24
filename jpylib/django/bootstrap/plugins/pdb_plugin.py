"""
Contains a plugin that can be loaded up with Django
the instantiates a signal that can enter a pdb session.
If we're debugging, it will also override the sys.excepthook
to allow for an interactive debugger.
"""
import code
import pdb
import signal
import sys
import traceback

from django.conf import settings


def except_hook(type, value, tb):
    """
    Exception hook for debugging any exceptions that
    happen in debugging
    """
    checks = [hasattr(sys, 'ps1'),
              not sys.stderr.isatty(),
              type == SystemExit]

    if any(checks):
        # we are in interactive mode or we don't have a tty-like
        # device, so we call the default hook.  Also, don't
        # drop into post mortem if SystemExit was thrown
        sys.__excepthook__(type, value, tb)

    else:
        # Not in interactive mode, print exception
        traceback.print_exception(type, value, tb)
        print
        # then start postmortem debugger
        pdb.post_mortem(tb)


def signal_hook(sig, frame):
    """
    Hooks into a SIGUSR1 signal from the os to
    allow an interactive debugger at a certain point.

    :param sig: the signal we sent in. should be signal.SIGUSR1
    :type sig: signal.SIGUSR1
    :param frame: The current frame of execution
    """
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    try:
        import rpdb2; rpdb2.start_embedded_debugger('UNIFIED!!!')
    except:
        i = code.InteractiveConsole(d)
        message  = "Signal received : entering python shell.\nTraceback:\n"
        message += ''.join(traceback.format_stack(frame))
        i.interact(message)

# Hook our signal hook up to listen for the SIGUSR1 signal
signal.signal(signal.SIGUSR1, signal_hook)

if settings.DEBUG and getattr(settings, 'PDB_DEBUG', True):
    # If we're debugging and we're allowing PDB, set exception hook
    sys.excepthook = except_hook
elif not settings.DEBUG and hasattr(pdb, 'disable'):
    # If DEBUG is not set, disable pdb set_trace, if using pdbpp
    pdb.disable()

