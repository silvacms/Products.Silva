# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $
# Zope
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
# Silva
from Products.Silva import mangle
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
# misc
from Products.Silva.helpers import add_and_edit
import urlparse

from interfaces import IContent, IContainer

#icon = "www/silvasemighost.gif"

class SemiGhost(Content, SimpleItem):
    """the first published document in ghost's container will be haunted"""
    
    security = ClassSecurityInfo()
    meta_type = "Silva Semi Ghost"
    __implements__ = IContent
    
    def _get_content(self):
        """returns first published content object

            if there is no published content object None is returned
        """
        for content_object in self.aq_parent.get_ordered_publishables():
            if content_object.is_published():
                return content_object
        return None 

    def render_preview(self):
        """Render preview of this version (which is what we point at)
        """
        content = self._get_content()
        if content is None:
            return None # public render code of ghost should give broken message
        else:
            return content.view()

    def render_view(self):
        """Render view of this version (which is what we point at)
        """
        return self.render_preview()

InitializeClass(SemiGhost)

manage_addSemiGhostForm = PageTemplateFile("www/semiGhostAdd", globals(),
   __name__='manage_addSemiGhostForm')

def manage_addSemiGhost(self, id, title='', REQUEST=None):
    """Add a Semi Ghost."""
    if not mangle.Id(self, id).isValid():
        return
    object = SemiGhost(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''

