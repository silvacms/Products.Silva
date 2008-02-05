# Copyright (c) 2003-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.8 $

from zope.interface import implements

# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
# Silva
from Content import Content
from interfaces import IContent
import SilvaPermissions
from helpers import add_and_edit
from Products.Silva import mangle

icon="www/silvageneric.gif"

class SimpleContent(Content, SimpleItem):
    """Utterly simple content.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Simple Content"

    implements(IContent)

    def is_deletable(self):
        """this is always deletable"""
        return 1

InitializeClass(SimpleContent)

manage_addSimpleContentForm = PageTemplateFile(
    "www/simpleContentAdd", globals(),
    __name__='manage_simpleContentForm')

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add a Simple Content object"""
    if not mangle.Id(self, id).isValid():
        return
    object = SimpleContent(id, title)
    self._setObject(id, object)
    content = self._getOb(id)
    content.set_title(title)
    
    add_and_edit(self, id, REQUEST)
    return ''
