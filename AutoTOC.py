# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: AutoTOC.py,v 1.12 2005/08/05 16:00:26 kitblake Exp $

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
from Products.Silva.i18n import translate as _
from Products.Silva.interfaces import IContent, IContainerPolicy
from Products.Silva.helpers import add_and_edit

icon = "www/autotoc.png"
addable_priority = 2

class AutoTOC(Content, SimpleItem):
    __doc__ = _("""This is a special document that automagically displays a
       table of contents. Usually it&#8217;s used as an &#8216;index&#8217;
       document. In that case the parent folder shows a table of contents
       when accessed (e.g. http://www.x.yz/silva/myFolder/).""")

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
        code, toc, etc.
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
