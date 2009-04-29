
def allow_translate():
    """Allow the importing and use of the zope.i18n.translate function
    in page templates.
    """
    from AccessControl import allow_module
    # XXX is this opening up too much..?
    allow_module('zope.i18n')

#Zope 2.10 contains a ZCatalog bug which causes
# folders to be unindexed twice when a parent
# container is removed.
# see: https://bugs.launchpad.net/silva/+bug/101780
# XXX NOTE: this needs to be removed once the bug is
#           fixed in ZCatalog
def fixupCatalogPathAwareness():
    from Products.ZCatalog.CatalogPathAwareness import CatalogPathAware
    def manage_beforeDelete(self, item, container):
        self.unindex_object()
    CatalogPathAware.manage_beforeDelete = manage_beforeDelete
    
def patch_all():
    # perform all patches
    allow_translate()
    fixupCatalogPathAwareness()
