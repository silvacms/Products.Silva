# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: GhostFolder.py,v 1.1 2003/07/22 10:05:08 zagy Exp $

#zope
import OFS.Folder
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile


# silva
from Products.Silva.Folder import Folder
from Products.Silva import SilvaPermissions
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.helpers import add_and_edit

from Products.Silva.interfaces import IContainer, IContent


icon = ''

class GhostFolder(Folder):
    """GhostFolders are used to haunt folders."""

    meta_type = 'Silva Ghost Folder'
    __implements__ = IContainer
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted_folder')
    def set_haunted_folder(self, path):
        """set the folder to be haunted"""
        folder = self.getPhysicalRoot().restrictedTraverse(path)
        self._haunted_folder = folder
        self.haunt()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunt')
    def haunt(self):
        """populate the the ghost folder with ghosts
        """
        haunted = self._haunted_folder
        ghost = self
        assert IContainer.isImplementedBy(haunted)
        object_list = [(h, ghost) for h in haunted.objectValues()]
        while object_list:
            haunted, ghost = object_list[0]
            del(object_list[0])
            old_ghost = getattr(ghost, haunted.id, None)
            if IContainer.isImplementedBy(haunted):
                if old_ghost is not None:
                    if IContainer.isImplementedBy(old_ghost):
                        new_ghost = old_ghost
                    else:
                        ghost.manage_delObjects([haunted.id])
                        old_ghost = None
                if old_ghost is None:
                    new_ghost = Folder(haunted.id)
                    ghost._setObject(haunted.id, new_ghost)
                    new_ghost = getattr(ghost, haunted.id)
                object_list += [(h, new_ghost)
                    for h in haunted.objectValues()]
            elif IContent.isImplementedBy(haunted):
                if haunted.meta_type == 'Silva Ghost':
                    version = self._get_version_from_ghost(haunted)
                    content_url = version.get_content_url()
                else:
                    content_url = '/'.join(haunted.getPhysicalPath())
                if old_ghost is not None:
                    if old_ghost.meta_type == 'Silva Ghost':
                        old_ghost.create_copy()
                        version = self._get_version_from_ghost(old_ghost)
                        version.set_content_url(content_url)
                    else:
                        ghost.manage_delObjects([haunted.id])
                        old_ghost = None
                if old_ghost is None:
                    manage_addGhost(ghost, haunted.id, content_url)
            
    def _get_version_from_ghost(self, ghost):
        """returns `latest' version of ghost

            ghost: Silva Ghost intance
            returns GhostVersion
        """
        assert ghost.meta_type == 'Silva Ghost'
        version_id = ghost.get_public_version()
        if version_id is None:
            version_id = ghost.get_next_version()
        if version_id is None:
            version_id = ghost.get_last_closed_version()
        version = getattr(ghost, version_id)
        return version
        
InitializeClass(GhostFolder)

    
manage_addGhostFolderForm = PageTemplateFile("www/ghostFolderAdd", globals(),
    __name__='manage_addGhostFolderForm')


def manage_addGhostFolder(dispatcher, id, REQUEST=None):
    """Add a GhostFolder"""
    haunted = REQUEST.get('haunt')
    gf = GhostFolder(id)
    dispatcher._setObject(id, gf)
    gf = getattr(dispatcher, id)
    gf.set_haunted_folder(haunted)
    add_and_edit(dispatcher, id, REQUEST)
    return ''

