# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.29 $
# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
# Silva interfaces
from IPublication import IPublication
# Silva
from Publication import Publication
import SilvaPermissions
import install
# misc
from helpers import add_and_edit

icon="www/silvageneric.gif"

class Root(Publication):
    """Root of Silva site.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Root"

    __implements__ = IPublication

    # MANIPULATORS

    def manage_afterAdd(self, item, container):
        # since we're root, we don't want to notify our container
        pass
        
    def manage_beforeDelete(self, item, container):
        # since we're root, we don't want to notify our container
        pass

    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_root')
    def get_root(self):
        """Get root of site. Can be used with acquisition get the
        'nearest' Silva root.
        """
        return self.aq_inner

    # FIXME: should be renamed to something else, indicating we get a url
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'silva_root')
    def silva_root(self):
        """Get url of root of site.
        """
        return self.aq_inner.absolute_url()
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        """Render object to XML.
        """
        f = context.f
        f.write('<silva_root id="%s">' % self.id)
        self._to_xml_helper(context)
        f.write('</silva_root>')

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_silva_addables_allowed_in_publication')
    def get_silva_addables_allowed_in_publication(self):
        # allow everything in silva by default, unless things are restricted
        # explicitly
        addables = self._addables_allowed_in_publication
        if addables is None:
            return self.get_silva_addables_all()
        else:
            return addables
    
InitializeClass(Root)

manage_addRootForm = PageTemplateFile("www/rootAdd", globals(),
                                      __name__='manage_addRootForm')

def manage_addRoot(self, id, title, REQUEST=None):
    """Add a Silva root."""
    # no id check possible or necessary, as this only happens rarely and the
    # Zope id check is fine
    object = Root(id, title)
    self._setObject(id, object)
    object = getattr(self, id)

    # now set it all up
    install.installFromScratch(object)

    add_and_edit(self, id, REQUEST)
    return ''
