# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

# Zope
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
# Silva
from Content import Content
from interfaces import IContent
from helpers import add_and_edit

icon="www/silvageneric.gif"

class SimpleContent(Content, SimpleItem):
    """Utterly simple content.
    """
    security = ClassSecurityInfo()
    
    meta_type = "Silva Simple Content"

    __implements__ = IContent

InitializeClass(SimpleContent)

manage_addSimpleContentForm = PageTemplateFile(
    "www/simpleContentAdd", globals(),
    __name__='manage_simpleContentForm')

def manage_addSimpleContent(self, id, title, REQUEST=None):
    """Add a Simple Content object"""
    if not self.is_id_valid(id):
        return
    object = SimpleContent(id, title)
    self._setObject(id, object)
    add_and_edit(self, id, REQUEST)
    return ''
