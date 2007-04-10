
def allow_translate():
    """Allow the importing and use of the zope.i18n.translate function
    in page templates.
    """
    from AccessControl import allow_module
    # XXX is this opening up too much..?
    allow_module('zope.i18n')
    
def patch_all():
    # perform all patches
    allow_translate()
