# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.57 $
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
from Version import Version
import SilvaPermissions
# misc
from helpers import add_and_edit
import urlparse

icon = "www/silvaghost.gif"

class Ghost(VersionedContent):
    """Ghosts are special documents wich function as a
       placeholder for an object in another location (like an alias,
       symbolic link, shortcut). Unlike a hyperlink, which takes the
       Visitor to another location, a ghost object keeps the Visitor in the
       current publication, and presents the content of the ghosted item.
       The ghost object inherits properties from its location (e.g. layout 
       and stylesheets).  
    """
    
    security = ClassSecurityInfo()

    meta_type = "Silva Ghost"

    __implements__ = IVersionedContent
    
    def __init__(self, id):
        Ghost.inheritedAttribute('__init__')(self, id)
    
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

class GhostVersion(Version):
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
        GhostVersion.inheritedAttribute('__init__')(
            self, id, '[Ghost title bug]')
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Don't do a thing.
        """
        pass

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_title')
    def get_title(self):
        """Get title.
        """        
        content = self._get_content()
        if content is None:
            return "Ghost target is broken"
        else:
            return content.get_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short title.
        """        
        content = self._get_content()
        if content is None:
            return "Ghost target is broken"
        else:
            short_title = content.get_short_title()
        if not short_title:
            return self.get_title()
        return short_title

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_content_url')
    def set_content_url(self, content_url):
        """Set content url.
        """
        # simplify url
        scheme, netloc, path, parameters, query, fragment = \
                urlparse.urlparse(content_url)        
        path_elements = path.split('/')

        # Cut off 'edit' and anything after it
        try:
            idx = path_elements.index('edit')
        except ValueError:
            pass
        else:
            path_elements = path_elements[:idx]

        content_url = '/'.join(path_elements)

        if path_elements[0] == '':
            # absolute, so traverse relatively from silva root
            traversal_root = silva_root = self.get_root()
            silva_root_url = '/' + silva_root.absolute_url(1)

            if not silva_root_url.endswith('/'):
                silva_root_url = silva_root_url + '/'            

            # Cut the 'silva root url' part off from the content url.
            # This will result in a relative (to the silva root) path
            # to the object            
            if content_url.startswith(silva_root_url):
                # replace only first occurence
                content_url = content_url.replace(silva_root_url, '', 1)
        else:
            # relative, so traverse from ghost's container:
            traversal_root = self.get_container()               

        # Now resolve it...
        try:
            target = traversal_root.unrestrictedTraverse(content_url)
            # ...and get physical path for it
            self._content_path = target.getPhysicalPath()
        except (AttributeError, KeyError):
            # ...or, in case of errors, set it to the raw input
            #
            # AttributeError is what unrestrictedTraverse raises
            # if it can find an object, but not its attribute.
            # KeyError is what unrestrictedTraverse raises
            # if it cannot find the object.
            self._content_path = path_elements
        
    def get_content_url(self):
        """Get content url.
        """
        if self._content_path is None:
            return None
        try: 
            object = self.get_root().unrestrictedTraverse(self._content_path)
            return '/' + object.absolute_url(1)
        except (AttributeError, KeyError):
            # AttributeError is what unrestrictedTraverse raises
            # if it can find an object, but not its attribute.
            # KeyError is what unrestrictedTraverse raises
            # if it cannot find the object.
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
        except (AttributeError, KeyError):
            return self.LINK_VOID
        if IContainer.isImplementedBy(content):
            return self.LINK_FOLDER
        if not IVersionedContent.isImplementedBy(content):
            return self.LINK_NO_CONTENT
        if content.meta_type == 'Silva Ghost':
            return self.LINK_GHOST

        return self.LINK_OK

    def _get_content_object(self, path):
        """Get content object for a url.
        """
        # XXX what if we're pointing to something that cannot be viewed
        # publically?
        if path is None:
            return None
        # XXX should this be a bare exception? catch all traversal failures
        try:
            content = self.unrestrictedTraverse(path)
        except:
            return None
        # Not allowed to ghost to a ghost or a container
        if (not IVersionedContent.isImplementedBy(content) or    
            content.meta_type == 'Silva Ghost'):
            return None
        return content
    
    def _get_content(self):
        """Get the real content object.
        """
        path = self._content_path
        return self._get_content_object(path)

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
            self.REQUEST.set('ghost_model', self.aq_inner)
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
            self.REQUEST.set('ghost_model', self.aq_inner)
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

def manage_addGhostVersion(self, id,REQUEST=None):
    """Add a Ghost version."""
    object = GhostVersion(id)
    self._setObject(id, object)
    object.set_content_url(content_url)
    add_and_edit(self, id, REQUEST)
    return ''
