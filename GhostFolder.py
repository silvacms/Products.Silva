# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: GhostFolder.py,v 1.15 2003/08/27 08:40:06 zagy Exp $

from __future__ import nested_scopes

#zope
import OFS.Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime


# silva
from Products.Silva import Folder
from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import GhostBase
from Products.Silva.helpers import add_and_edit
from Products.Silva import mangle
from Products.Silva.Metadata import export_metadata
from Products.Silva.Publishable import Publishable
from Products.Silva.Versioning import VersioningError

from Products.Silva.interfaces import \
    IContainer, IContent, IAsset, IGhost, IPublishable, IVersionedContent, \
    IPublication, ISilvaObject

icon = 'www/silvaghostfolder.gif'

class GhostFolder(GhostBase, Publishable, Folder.Folder):
    """GhostFolders are used to haunt folders."""

    meta_type = 'Silva Ghost Folder'
    __implements__ = IContainer, IGhost
    security = ClassSecurityInfo()

    _active_flag = 1

    def __init__(self, id):
        GhostFolder.inheritedAttribute('__init__')(self, id)
        self._content_path = None

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunt')
    def haunt(self):
        """populate the the ghost folder with ghosts
        """
        # XXX: this method is to long and should be splitted
        haunted = self._get_content()
        if haunted is None:
            return
        if self.get_link_status() != self.LINK_OK:
            return
        ghost = self
        assert IContainer.isImplementedBy(haunted)
        object_list = self._haunt_diff(haunted, ghost)
        
        while object_list:
            # breadth first search
            h_container, h_id, g_container, g_id = object_list[0]
            del(object_list[0])
            if h_id is None:
                # object was removed from haunted, so just remove it and 
                # continue
                g_container.manage_delObjects([g_id])
                continue
            h_ob = h_container._getOb(h_id)
            if g_id is None:
                # object was added to haunted
                g_ob = None
            else:
                # object is there but may have changed
                g_ob = g_container._getOb(g_id)
            if IContainer.isImplementedBy(h_ob):
                if g_ob is not None:
                    if IContainer.isImplementedBy(g_ob):
                        # no need to change
                        g_ob_new = g_ob
                    else:
                        g_container.manage_delObjects([h_id])
                        g_ob = None
                if g_ob is None:
                    ghost.manage_addProduct['Silva'].manage_addFolder(
                        h_id, '[no title]', 0)
                    g_ob_new = g_container._getOb(h_id)
                object_list += self._haunt_diff(h_ob, g_ob_new)
            elif IContent.isImplementedBy(h_ob):
                if h_ob.meta_type == 'Silva Ghost':
                    content_url = h_ob.get_content_url()
                else:
                    content_url = '/'.join(h_ob.getPhysicalPath())
                if g_ob is not None:
                    if g_ob.meta_type == 'Silva Ghost':
                        # we already have a ghost sitting there, create a new
                        g_ob.create_copy()
                        version = g_ob.getLastVersion()
                        version.set_content_url(content_url)
                    else:
                        g_container.manage_delObjects([h_id])
                        g_ob = None
                if g_ob is None:
                    g_container.manage_addProduct['Silva'].manage_addGhost(
                     h_id, content_url)
            else:
                # this is anything else -- copy it. We cannot check if it was 
                # modified and if copying is really necessary.
                if g_ob is not None:
                    g_container.manage_delObjects([h_id])
                g_ob_new = h_ob._getCopy(g_container)
                g_container._setObject(h_id, g_ob_new)
        self._publish_ghosts()
        self._invalidate_sidebar(self)

    def _haunt_diff(self, haunted, ghost):
        h_ids = list(haunted.objectIds())
        g_ids = list(ghost.objectIds())
        h_ids.sort()
        g_ids.sort()
        ids = []
        while h_ids or g_ids:
            h_id = None
            g_id = None
            if h_ids:
                h_id = h_ids[0]
            if g_ids:
                g_id = g_ids[0]
            if h_id == g_id or h_id is None or g_id is None:
                ids.append((h_id, g_id))
                if h_ids:
                    del h_ids[0]
                if g_ids:
                    del g_ids[0]
            elif h_id < g_id:
                ids.append((h_id, None))
                del h_ids[0]
            elif h_id > g_id:
                ids.append((None, g_id))
                del g_ids[0]
        objects = [ (haunted,h_id, ghost, g_id)
            for (h_id, g_id) in ids ]
        return objects
        

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
        app = self.getPhysicalRoot()
        while chain:
            ancestor = chain[0]
            del(chain[0])
            if ancestor is app:
                # anything farther up the tree is not `referencable'. 
                chain = []
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
        f.write("</silva_ghostfolder>")
    
    
    # all this is for a nice side bar
    def is_transparent(self):
        """show in subtree? depends on haunted object"""
        content = self._get_content()
        if IContainer.isImplementedBy(content):
            return content.is_transparent()
        return 0
    
    def get_publication(self):
        """returns self if haunted object is a publication"""
        content = self._get_content()
        if IPublication.isImplementedBy(content):
            return self.aq_inner
        return self.aq_inner.aq_parent.get_publication()

    def implements_publication(self):
        content = self._get_content()
        if ISilvaObject.isImplementedBy(content):
            return content.implements_publication()
        return 0

    def is_deletable(self):
        return 1

    def _publish_ghosts(self, activate=1):
        activate_list = self.get_ordered_publishables()
        # ativate all containing objects, depth first
        while activate_list:
            object = activate_list.pop()
            if IContainer.isImplementedBy(object):
                activate_list += object.get_ordered_publishables()
            if IVersionedContent.isImplementedBy(object):
                if activate:
                    object.create_copy()
                    object.set_unapproved_version_publication_datetime(
                        DateTime())
                    object.approve_version()
                else:
                    object.close_version()
                    
    def _factory(self, container, id, content_url):
        return container.manage_addProduct['Silva'].manage_addGhostFolder(id,
            content_url)
       
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
    return ghostfolder
       
