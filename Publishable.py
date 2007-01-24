# Copyright (c) 2002-2007 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.25 $
from zope.interface import implements
# Zope
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
# Silva 
import SilvaPermissions
# misc
import helpers

from interfaces import IPublishable, IContent, IVersioning, IContainer
from interfaces import IPublication

class Publishable:
    """Mixin class that can be provided to implement the Publishable
    interface.
    """
    security = ClassSecurityInfo()
        
    implements(IPublishable)

    _active_flag = 1

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'activate')
    def activate(self):
        if not self.can_activate():
            return
        self._active_flag = 1
        # refresh container of parent (may be parent itself)
        # we use parent so we don't get *this* publishable container
        self.aq_parent.get_container()._refresh_ordered_ids(self)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'deactivate')
    def deactivate(self):
        if not self.can_deactivate():
            return
        # we can deactivate, but we should unapprove everything that
        # is approved
        helpers.unapprove_helper(self)
        # now set the flag
        self._active_flag = 0
        # refresh container of parent (may be parent itself)
        # we use parent so we don't get *this* publishable container
        self.aq_parent.get_container()._refresh_ordered_ids(self)
        
    # ACCESSORS

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_active')
    def is_active(self):
        return self._active_flag

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'can_activate')
    def can_activate(self):
        return not self._active_flag

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'can_deactivate')
    def can_deactivate(self):
        if not self._active_flag:
            return 0
        # can't deactivate default
        if IContent.providedBy(self) and self.is_default():
            return 0
        # can't deactivate something published
        if self.is_published():
            return 0
        return 1

    # FIXME: perhaps make this less public?
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'is_published')
    def is_published(self):
        if IVersioning.providedBy(self):
            return self.is_version_published()
        else:
            return 1

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'is_approved')
    def is_approved(self):
        if IVersioning.providedBy(self):
            return self.is_version_approved()
        else:
            # never be approved if there is no versioning
            return 0

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
        'is_deletable')
    def is_deletable(self):
        """is object deletable?
        
            a publishable object is only deletable if
                it's not published
                it's not approved
        
        """
        return not self.is_published() and not self.is_approved()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """Analogous to is_deletable() (?)
        """
        return not self.is_published() and not self.is_approved()
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'can_approve')
    def can_approve(self):
        """Return true if we can approve version.
        NOTE: this method is defined by the Versioning interface, but
        this is the default implementation for versioned publishables.
        """
        # if this object or any of its containers is inactive, can't approve it        
        if not self.is_active():
            return 0
        # check all containers to see if they are inactive as well
        object = self.aq_parent
        while IContainer.providedBy(object):
            if not object.is_active():
                return 0
            object = object.aq_parent
        # all containers were active, so we can indeed approve
        return 1

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_real_container')
    def get_real_container(self):
        """Get the container, even if we're a container.

        If we're the root object, returns None.
        
        Can be used with acquisition to get the 'nearest' container.
        """
        return self.get_container() 
    
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_document_navigation_links')
    def get_document_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.
        
        This can be used by Mozilla in the accessibility toolbar.
        """
        # we need get_real_container as we want the container
        # *even if* we are a container ourselves
        container = self.get_real_container()
        # if we're in the root, we can't navigate
        if container is None:
            return {}

        if IContent.providedBy(self) and self.is_default():
            return container.get_document_navigation_links()
        
        result = { 'up': '..' }
        links = {}
        objects = []
        object_ids = []

        top = self.get_publication()
        if top is not self:
            result['top'] = top#.absolute_url()
            
        tree = container.get_public_tree(0)
        for depth, obj in tree:
            if obj.meta_type == 'Silva AutoTOC':
                continue
            if obj.meta_type == 'Silva Indexer':
                continue
            object_ids.append(obj.id)
            objects.append(obj)
       
        # something bad happens
        # could be, that we're calling this method from an Indexer, so
        # return nothing 
        try:
            i = object_ids.index(self.id)
        except ValueError:
            return {}

        first = 0
        previous = i - 1
        next = i + 1
        last = len(object_ids) - 1

        if i != first:
            links['first'] = first
        if i != last:
            links['last'] = last
        if previous >= first:
            links['prev'] = previous
        if next <= last:
            links['next'] = next

        for key, value in links.items():
            links[key] = objects[value]#.absolute_url()
            
        result.update(links)
        return result

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_navigation_links')
    def get_navigation_links(self):
        """
        Create a dictionary with top, up, first, previous, next, last links.
        
        This can be used by Mozilla in the accessibility toolbar.
        """
        
        top = self.get_publication()
        result = {}
        next = self.get_navigation_next()
        prev = self.get_navigation_prev()
        last = self.get_navigation_last()
        
        if top is not self:
            result['top'] = top
            result['first'] = top
            result['up'] = ".."
        

        if last.id != self.id:
            result['last'] = last
        
        if next is not None:
            result['next'] = next

        if prev is not None:
            result['prev'] = prev

        return result
    

    def get_navigation_prev(self):
        """ Returns the prev object in the publication tree """
        node = self
        top = self.get_publication()
        
        if self is top:
            return None
            
        while 1:
            if node is top:
                return node
            if IContainer.providedBy(node):
                container = node.aq_parent
            container = node.aq_parent 
            #objects = container.get_public_tree(0)
            objects = container.get_public_tree_helper(0)
            object_ids = [object.id for depth, object in objects]
            try:
                i = object_ids.index(self.id)
            except ValueError:
                return container

            prev_i = i-1
           
            # there is no previous in a folder, so check if node is a
            # folder or not
            if prev_i == -1:
                return container
            elif prev_i >= 0 and IContainer.providedBy(objects[prev_i][1]):
                return self._get_last_helper(objects[i-1][1])
    
            if prev_i >= 0:
                return objects[prev_i][1]
            
            node = container
    
    def get_navigation_next(self):
        """ Returns the next object in the Publication tree """
        node = self
        top = self.get_publication()
        if IContainer.providedBy(node):
            #objects = node.get_public_tree(0)
            objects = node.get_public_tree_helper(0)
            if objects:
                return objects[0][1]
        
        while 1:
            if self is top:
                return None
            
            container = node.aq_parent
            objects = node.get_public_tree_helper(0)
            object_ids = [object.id for depth, object in objects]
            try:
                i = object_ids.index(self.id)
            except ValueError:
                if not object_ids:
                    self = node
                    node = container 
                    continue
                else:
                    return objects[0][1]
                    

            next_i = i+1
            
            if next_i < len(objects):
                return objects[next_i][1]
            
            self = node
            node = container
            
    def get_public_tree_helper(self, depth):
        """ wrapper method for get_public_tree()
            returns the public tree without any publications 
        """
        public_tree = []
        tree = self.get_public_tree(depth)
        for item in tree:
            if IPublication.providedBy(item[1]):
                continue
            else:
                public_tree.append(item)

        return public_tree
            
    def get_navigation_last(self):
        """ Returns the last object in the publication tree """
        node = self.get_publication()
        return self._get_last_helper(node)

    def _get_last_helper(self, root):
        """ returns the last object in a tree """
        node = root
        while 1:
            if IContent.providedBy(node):
                return node
            if IContainer.providedBy(node):
                objects = node.get_public_tree(0)
                if not objects:
                    return node 
                
                node = objects[-1][1]
        
             
InitializeClass(Publishable)
