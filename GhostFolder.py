# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: GhostFolder.py,v 1.7 2003/08/06 09:06:26 zagy Exp $

#zope
import OFS.Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime


# silva
from Products.Silva import Folder
from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import GhostBase, getLastVersionFromGhost
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Metadata import export_metadata
from Products.Silva.Publishable import Publishable
from Products.Silva.Versioning import VersioningError

from Products.Silva.interfaces import \
    IContainer, IContent, IAsset, IGhost, IPublishable, IVersionedContent

icon = 'www/silvaghost.gif'

class GhostFolder(GhostBase, Publishable, Folder.Folder):
    """GhostFolders are used to haunt folders."""

    meta_type = 'Silva Ghost Folder'
    __implements__ = IContainer, IGhost, IPublishable
    security = ClassSecurityInfo()

    _active_flag = 0

    def set_content_url(self, content_url):
        GhostFolder.inheritedAttribute('set_content_url')(self, content_url)
        self.haunt()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunt')
    def haunt(self):
        """populate the the ghost folder with ghosts
        """
        haunted = self._get_content()
        if haunted is None:
            return
        if self.get_link_status() != self.LINK_OK:
            return
        ghost = self
        assert IContainer.isImplementedBy(haunted)
        object_list = [(h, ghost) for h in haunted.objectValues()]
        while object_list:
            haunted, ghost = object_list[0]
            del(object_list[0])
            if hasattr(ghost.aq_base, haunted.id):
                old_ghost = getattr(ghost, haunted.id, None)
            else:
                old_ghost = None
            if IContainer.isImplementedBy(haunted):
                if old_ghost is not None:
                    if IContainer.isImplementedBy(old_ghost):
                        new_ghost = old_ghost
                    else:
                        ghost.manage_delObjects([haunted.id])
                        old_ghost = None
                if old_ghost is None:
                    ghost.manage_addProduct['Silva'].manage_addFolder(
                        haunted.id, '[no title]')
                    new_ghost = getattr(ghost, haunted.id)
                object_list += [(h, new_ghost)
                    for h in haunted.objectValues()]
            elif IContent.isImplementedBy(haunted):
                if haunted.meta_type == 'Silva Ghost':
                    version = getLastVersionFromGhost(haunted)
                    content_url = '/'.join(
                        version._get_content().getPhysicalPath())
                else:
                    content_url = '/'.join(haunted.getPhysicalPath())
                if old_ghost is not None:
                    if old_ghost.meta_type == 'Silva Ghost':
                        old_ghost.create_copy()
                        version = getLastVersionFromGhost(old_ghost)
                        version.set_content_url(content_url)
                    else:
                        ghost.manage_delObjects([haunted.id])
                        old_ghost = None
                if old_ghost is None:
                    ghost.manage_addProduct['Silva'].manage_addGhost(
                     haunted.id, content_url)
            else:
                if old_ghost is not None:
                    ghost.manage_delObjects([haunted.id])
                new_ghost = haunted._getCopy(ghost)
                ghost._setObject(haunted.id, new_ghost)
                
    security.declareProtected(SilvaPermissions.View,'get_link_status')
    def get_link_status(self, content=None):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        if content is None:
            content = self._get_content(check=0)
        if self._content_path is None:
            return self.LINK_EMPTY
        if content is None:
            return self.LINK_VOID
        if IGhost.isImplementedBy(content):
            return self.LINK_GHOST
        if IContent.isImplementedBy(content):
            return self.LINK_CONTENT
        if not IContainer.isImplementedBy(content):
            return self.LINK_NO_FOLDER
        if self.isReferencingSelf(content):
            return self.LINK_CIRC
        return self.LINK_OK
                
    def isReferencingSelf(self, content=None):
        """returns True if ghost folder references self or a ancestor of self
        """
        if content is None:
            content = self._get_content(check=0)
        if content is None:
            # if we're not referncing anything it is not a circ ref for sure
            return 0
        content_path = content.getPhysicalPath()
        chain = self.aq_chain[:]
        while chain:
            ancestor = chain[0]
            del(chain[0])
            if ancestor.getPhysicalPath() == content_path:
                return 1
        return 0

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'to_publication')
    def to_publication(self):
        """replace self with a folder"""
        self._to_folder_or_publication_helper(to_folder=0)
        
    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'to_folder')
    def to_folder(self):
        """replace self with a folder"""
        self._to_folder_or_publication_helper(to_folder=1)

    def to_xml(self, context):
        f = context.f
        f.write("<silva_ghostfolder id='%s' content_url='%s'>" % (
            self.getId(), self.get_content_url()))
        self._to_xml_helper(context)
        export_metadata(self._get_content(), context)
        f.write("</silva_ghostfolder>")
       

    # Publishable 
    
    def activate(self):
        """activate self and publish containing objects"""
        self._activate_helper(activate=1)
        GhostFolder.inheritedAttribute('activate')(self)
    
    def deactivate(self):
        """deactivate self and close containing objects"""
        self._activate_helper(activate=0)
        GhostFolder.inheritedAttribute('deactivate')(self)

    
    def _activate_helper(self, activate=1):
        activate_list = self.get_ordered_publishables()
        # ativate all containing objects, depth first
        while activate_list:
            object = activate_list.pop()
            if IContainer.isImplementedBy(object):
                activate_list += object.get_ordered_publishables()
            if IPublishable.isImplementedBy(object):
                if activate:
                    object.activate()
                else:
                    object.deactivate()
            if IVersionedContent.isImplementedBy(object):
                if activate:
                    object.create_copy()
                    object.set_unapproved_version_publication_datetime(
                        DateTime())
                    object.approve_version()
                else:
                    object.close_version()
                    

       
InitializeClass(GhostFolder)

    
manage_addGhostFolderForm = PageTemplateFile("www/ghostFolderAdd", globals(),
    __name__='manage_addGhostFolderForm')


def manage_addGhostFolder(dispatcher, id, content_url, REQUEST=None):
    """Add a GhostFolder"""
    if not mangle.Id(dispatcher, id).isValid():
        return
    gf = GhostFolder(id)
    dispatcher._setObject(id, gf)
    gf = getattr(dispatcher, id)
    gf.set_content_url(content_url)
    add_and_edit(dispatcher, id, REQUEST)
    return ''

def xml_import_handler(object, node):

    def _get_content_url(node):
        content_url = node.attributes.getNamedItem('content_url').nodeValue
        assert type(content_url) == type(u''), \
            "got %r, expected a unicode" % content_url
        return content_url.encode('us-ascii', 'ignore')
    
    def factory(object, id, title, content_url):
        object.manage_addProduct['Silva'].manage_addGhostFolder(id,
            content_url)
    
    content_url = _get_content_url(node)
    f = lambda object, id, title, content_url=content_url: \
        factory(object, id, title, content_url)
    ghostfolder = Folder.xml_import_handler(object, node, factory=f)
    ghostfolder.haunt()
    return ghostfolder
       
