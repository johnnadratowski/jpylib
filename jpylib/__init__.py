"""
This is the Unified Python Standard Library top-level module
"""

def DynamicImportModule(module):
    """
    Dynamically imports the given module, so that it can be reloaded during runtime

    :param module: The module path that should be re-imported
    :type module: string
    :returns: The reloaded module
    """
    mod = __import__(module)
    components = module.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
