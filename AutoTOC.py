# Copyright (c) 2002-2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: AutoTOC.py,v 1.6 2004/07/21 11:40:40 jw Exp $

# Zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Persistence import Persistent
from OFS.SimpleItem import SimpleItem

# products
from Products.ParsedXML.ParsedXML import ParsedXML

# Silva
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from Products.Silva import mangle
from Products.Silva.interfaces import IContent, IContainerPolicy
from Products.Silva.helpers import add_and_edit

icon = "www/autotoc.png"
addable_priority = 2

class AutoTOC(Content, SimpleItem):
    """Automatically displays a table of contents. If it's named 'index', the parent folder will show a table of contents when requested (e.g. http://www.x.yz/silva/myFolder/)."""
    security = ClassSecurityInfo()

    meta_type = "Silva AutoTOC"

    __implements__ = IContent

    def __init__(self, id):
        AutoTOC.inheritedAttribute('__init__')(self, id,
            '[Title is stored in metadata. This is a bug.]')

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'is_cacheable')
    def is_cacheable(self):
        """Return true if this document is cacheable.
        That means the document contains no dynamic elements like
        code, datasource or toc.
        """
        return 0

    def is_deletable(self):
        """always deletable"""
        return 1

    def can_set_title(self):        
        """always settable"""
        # XXX: we badly need Publishable type objects to behave right.
        return 1
    
InitializeClass(AutoTOC)

manage_addAutoTOCForm = PageTemplateFile("www/autoTOCAdd", globals(),
    __name__='manage_addAutoTOCForm')

def manage_addAutoTOC(self, id, title, REQUEST=None):
    """Add a autotoc."""
    if not mangle.Id(self, id).isValid():
        return
    object = AutoTOC(id)
    self._setObject(id, object)
    object = getattr(self, id)
    object.set_title(title)
    add_and_edit(self, id, REQUEST)
    return ''

class AutoTOCPolicy(Persistent):

    __implements__ = IContainerPolicy

    def createDefaultDocument(self, container, title):
        container.manage_addProduct['Silva'].manage_addAutoTOC(
            'index', title)
        container.index.sec_update_last_author_info()
