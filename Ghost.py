# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.47 $
# Zope
from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
# Silva interfaces
from IVersionedContent import IVersionedContent
from IContainer import IContainer
# Silva
from VersionedContent import VersionedContent
import SilvaPermissions
# misc
from helpers import add_and_edit
import urlparse

icon = "www/silvaghost.gif"

class Ghost(VersionedContent):
    """Ghost object.
    """
    
    security = ClassSecurityInfo()

    meta_type = "Silva Ghost"

    __implements__ = IVersionedContent
    
    def __init__(self, id):
        Ghost.inheritedAttribute('__init__')(self, id, 'No title for ghost')
        
    def set_title(self, title):
        # FIXME: what to do here?
        pass
    
    def get_title(self):
        """Get title.
        """
        #return "Dummy ghost title" 
        ghost_version = self.get_viewable()
        if ghost_version is None:
	    ghost_version = self.get_previewable()
	    if ghost_version is None:
                return 'ghost target title not available'
        content = ghost_version._get_content()
        if content is None:
            return "Ghost target is broken"
        else:
            return content.get_title()

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'to_xml')
    def to_xml(self, context):
        if context.last_version == 1:
            version_id = self.get_next_version()
            if version_id is None:
                version_id = self.get_public_version()
        else:
            version_id = self.get_public_version()
        if version_id is None:
            return
        version = getattr(self, version_id)
        content = version._get_content()
        if content is None:
            return
        content.to_xml(context)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'update')
    def update(self):
        for object in self.objectValues():
            print object._content_url
            object.set_content_url(object._content_url)

    security.declarePrivate('get_indexables')
    def get_indexables(self):
        version = self.get_viewable()
        if version is None:
            return []
        content = version._get_content()
        if content is None:
            return []
        return content.get_indexables()

InitializeClass(Ghost)

class GhostVersion(SimpleItem.SimpleItem):
    """Ghost version.
    """
    meta_type = 'Silva Ghost Version'

    security = ClassSecurityInfo()

    # status codes:
    LINK_OK = None   # link is ok
    LINK_EMPTY = 1   # no link entered (XXX this cannot happen)
    LINK_VOID = 2    # object pointed to does not exist
    LINK_FOLDER = 3  # link points to folder
    LINK_GHOST = 4   # link points to another ghost
    LINK_NO_CONTENT = 5 # link points to something which is not a content
    

    def __init__(self, id):
        self.id = id

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_content_url')
    def set_content_url(self, content_url):
        """Set content url.
        """
        # FIXME: should never ever be allowed to point to a ghost
        # or a container - do a lot of tests (actually done in get_content_object)
        # simplify url
        scheme, netloc, path, parameters, query, fragment = \
                urlparse.urlparse(content_url)
        steps = path.split('/')
        # cut off anything after edit
        if len(steps) >= 2 and steps[-2] == 'edit':
            steps = steps[:-2]
        # cut off initial slash
        if steps[0] == '':
            steps = steps[1:]
        content_url = '/'.join(steps)
        # now resolve it
        try:
            object = self.unrestrictedTraverse(content_url)
            # and get physical path for it
            self._content_path = object.getPhysicalPath()
        except:
            # in case of errors, set it to the raw input
            steps.insert(0,'')
            self._content_path = steps
        
    def get_content_url(self):
        """Get content url.
        """
        if self._content_path is None:
            return None
	try: 
            object = self.unrestrictedTraverse(self._content_path)
            return '/' + object.absolute_url(1)
	except KeyError:
	    # KeyError is what unrestrictedTraverse raises if it cannot find the object
	    return '/'.join(self._content_path)

    security.declareProtected(SilvaPermissions.View,'get_link_status')
    def get_link_status(self):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        if self._content_path is None:
            return self.LINK_EMPTY
        try: 
            content = self.unrestrictedTraverse(self._content_path)
	except KeyError:
            return self.LINK_VOID
            return "The object &laquo;%s&raquo; the ghost points to does no longer exist" % '/'.join(self._content_path)
        if IContainer.isImplementedBy(content):
            return self.LINK_FOLDER
            return "The object &laquo;%s&raquo; the ghost points to is a container." % '/'.join(self._content_path)
        if not IVersionedContent.isImplementedBy(content):
            return self.LINK_NO_CONTENT
            return "The object &laquo;%s&raquo; the ghost points to is not a content object." % '/'.join(self._content_path)
        if content.meta_type == 'Silva Ghost':
            return self.LINK_GHOST
            return "The object &laquo;%s&raquo; the ghost points to is itself a ghost." % '/'.join(self._content_path)

        return self.LINK_OK


    def _get_content_object(self, path):
        """Get content object for a url.
        """
        # XXX what if we're pointing to something that cannot be viewed
        # publically?
        if url is None:
            return None
        # XXX should this be a bare exception? catch all traversal failures
        try:
            content = self.unrestrictedTraverse(url)
        except:
            return None
        
        if (not IVersionedContent.isImplementedBy(content) or    
            content.meta_type == 'Silva Ghost'):
            return None
        return content
    
    def _get_content(self):
        """Get the real content object.
        """
        # XXX what if we're pointing to something that cannot be viewed
        # publically?
        path = self._content_path
        if path is None:
            return None
        # XXX should this be a bare exception? catch all traversal failures
        try:
            content = self.unrestrictedTraverse(path)
        except:
            return None
        
        if (not IVersionedContent.isImplementedBy(content) or    
            content.meta_type == 'Silva Ghost'):
            return None    
        return content

    def render_preview(self):
        """Render preview of this version (which is what we point at)
        """
        # FIXME: should only call view if we are allowed to by content
        # FIXME what if content is None?
        # what if we get circular ghosts?
        content = self._get_content()
        if content is None:
            return None # public render code of ghost should give broken message
        else:
            return content.view()

    def render_view(self):
        """Render view of this version (which is what we point at)
        """
        # FIXME: should only call view if we are allowed to by content
        # FIXME what if content is None?
        # what if we get circular ghosts?
        content = self._get_content()
        if content is None:
            return None # public render code of ghost should give broken message
        else:
            return content.view()
    
manage_addGhostForm = PageTemplateFile("www/ghostAdd", globals(),
                                       __name__='manage_addGhostForm')

def manage_addGhost(self, id, content_url, REQUEST=None):
    """Add a Ghost."""
    if not self.is_id_valid(id):
        return
    object = Ghost(id)
    self._setObject(id, object)
    object = getattr(self, id)
    # add first version
    object._setObject('0', GhostVersion('0'))
    # we need to set content url after we created version, not
    # in constructor, as getPhysicalRoot() won't work there
    getattr(object, '0').set_content_url(content_url)
    object.create_version('0', None, None)
    add_and_edit(self, id, REQUEST)
    return ''

manage_addGhostVersionForm = PageTemplateFile("www/ghostversionAdd", globals(),
                                              __name__='manage_addGhostVersionForm')

def manage_addGhostVersion(self, id, REQUEST=None):
    """Add a Ghost version."""
    object = GhostVersion(id)
    self._setObject(id, object)
    object.set_content_url(content_url)
    add_and_edit(self, id, REQUEST)
    return ''
