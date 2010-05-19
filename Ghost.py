# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import urlparse

# Zope 3
from five import grok

# Zope 2
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from zExceptions import Unauthorized

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions
from Products.Silva.adapters.path import PathAdapter

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import (
    IContainer, IContent, IGhost, IGhostContent, IGhostVersion)
from silva.translations import translate as _


class GhostBase(object):
    """baseclas for Ghosts (or Ghost versions if it's versioned)
    """
    security = ClassSecurityInfo()

    # status codes as returned by get_link_status
    # NOTE: LINK_FOLDER (and alike) must *only* be returned if it is an error
    # for the link to point to a folder. If it is not an error LINK_OK must
    # be returned.
    LINK_OK = None   # link is ok
    LINK_EMPTY = 1   # no link entered (XXX this cannot happen)
    LINK_VOID = 2    # object pointed to does not exist
    LINK_FOLDER = 3  # link points to folder
    LINK_GHOST = 4   # link points to another ghost
    LINK_NO_CONTENT = 5 # link points to something which is not a content
    LINK_CONTENT = 6 # link points to content
    LINK_NO_FOLDER = 7 # link doesn't point to a folder
    LINK_CIRC = 8 # Link results in a ghost haunting itself

    # those should go away
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
        content = self.get_haunted_unrestricted()
        if content is None:
            return ("Ghost target is broken")
        else:
            return content.get_title()

    def get_title_editable(self):
        """Get title.
        """
        content = self.get_haunted_unrestricted()
        if content is None:
            return ("Ghost target is broken")
        else:
            return content.get_title_editable()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """title comes from haunted object
        """
        return False

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short title.
        """
        content = self.get_haunted_unrestricted()
        if content is None:
            return ("Ghost target is broken")
        else:
            short_title = content.get_short_title()
        if not short_title:
            return self.get_title()
        return short_title
    # /those should go away

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted_url')
    def set_haunted_url(self, content_url):
        """Set content url.
        """
        pad = PathAdapter(self.REQUEST)
        path = pad.urlToPath(content_url)

        path_elements = path.split('/')

        # Cut off 'edit' and anything after it
        try:
            idx = path_elements.index('edit')
        except ValueError:
            pass
        else:
            path_elements = path_elements[:idx]

        if path_elements[0] == '':
            traversal_root = self.get_root()
        else:
            traversal_root = self.get_container()

        # Now resolve it...
        target = traversal_root.unrestrictedTraverse(path_elements, None)
        if target is None:

            (scheme, netloc, path, parameters, query, fragment) = \
                                            urlparse.urlparse(content_url)
            self._content_path = path.split('/')
        else:
            # ...and get physical path for it
            self._content_path = target.getPhysicalPath()

    security.declareProtected(SilvaPermissions.View, 'get_haunted_url')
    def get_haunted_url(self):
        """Get content url.
        """
        if self._content_path is None:
            return None

        object = self.get_root().unrestrictedTraverse(self._content_path, None)
        if object is None:
            return '/'.join(self._content_path)

        pad = PathAdapter(self.REQUEST)
        url = pad.pathToUrlPath('/'.join(object.getPhysicalPath()))
        return url

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunted_path')
    def haunted_path(self):
        return self._content_path

    security.declareProtected(SilvaPermissions.View,'get_link_status')
    def get_link_status(self, content=None):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        raise NotImplementedError, "implemented in subclasses"

    def _get_object_at(self, path, check=1):
        """Get content object for a url.
        """
        # XXX what if we're pointing to something that cannot be viewed
        # publically?
        if path is None:
            return None
        content = self.aq_inner.aq_parent.unrestrictedTraverse(path, None)
        if content is None:
            return None
        # check if it's valid
        valid = None
        if check:
            valid = self.get_link_status(content)
        if valid is None:
            return content
        return None

    security.declarePrivate('get_haunted_unrestricted')
    def get_haunted_unrestricted(self, check=1):
        """Get the real content object.
        """
        return self._get_object_at(self._content_path, check)

    security.declareProtected(SilvaPermissions.View,'get_haunted')
    def get_haunted(self):
        """get the real content object; using restrictedTraverse

            returns content object, or None on traversal failure.
        """
        path = self._content_path
        return self.restrictedTraverse(path, None)


class Ghost(CatalogedVersionedContent):
    __doc__ = _("""Ghosts are special documents that function as a
       placeholder for an item in another location (like an alias,
       symbolic link, shortcut). Unlike a hyperlink, which takes the
       Visitor to another location, a ghost object keeps the Visitor in the
       current publication, and presents the content of the ghosted item.
       The ghost inherits properties from its location (e.g. layout
       and stylesheets).
    """)

    meta_type = "Silva Ghost"
    security = ClassSecurityInfo()

    grok.implements(IGhostContent)
    silvaconf.icon('icons/silvaghost.gif')
    silvaconf.versionClass('GhostVersion')


    def get_title_editable(self):
        """Get title for editable or previewable use
        """
        # Ask for 'previewable', which will return either the 'next version'
        # (which may be under edit, or is approved), or the public version,
        # or, as a last resort, the closed version.
        # This to be able to show at least some title in the Silva edit
        # screens.
        previewable = self.get_previewable()
        if previewable is None:
            return "[No title available]"
        return previewable.get_title_editable()

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'can_set_title')
    def can_set_title(self):
        """title comes from haunted object
        """
        return False

    security.declarePrivate('getLastVersion')
    def getLastVersion(self):
        """returns `latest' version of ghost

            ghost: Silva Ghost intance
            returns GhostVersion
        """
        version_id = self.get_public_version()
        if version_id is None:
            version_id = self.get_next_version()
        if version_id is None:
            version_id = self.get_last_closed_version()
        version = getattr(self, version_id)
        return version

    def get_haunted_url(self):
        """return content url of `last' version"""
        version = self.getLastVersion()
        return version.get_haunted_url()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'is_version_published')
    def is_version_published(self):
        public_id = self.get_public_version()
        if not public_id:
            return False
        public = getattr(self, public_id)
        haunted = public.get_haunted_unrestricted()
        if haunted is None:
            return False
        return haunted.is_published()

    def get_modification_datetime(self, update_status=1):
        """Return modification datetime."""
        super_method = Ghost.inheritedAttribute(
            'get_modification_datetime')
        content = self.getLastVersion().get_haunted_unrestricted()

        if content is not None:
            return content.get_modification_datetime(update_status)
        else:
            return super_method(self, update_status)

    def _factory(self, container, id, content_url):
        return container.manage_addProduct['Silva'].manage_addGhost(id,
            haunted_url=content_url)


InitializeClass(Ghost)


class GhostVersion(GhostBase, CatalogedVersion):
    """Ghost version.
    """
    meta_type = 'Silva Ghost Version'
    grok.implements(IGhostVersion)

    security = ClassSecurityInfo()

    def __init__(self, id):
        GhostVersion.inheritedAttribute('__init__')(
            self, id)
        self._content_path = None

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
       target = self.get_haunted_unrestricted()
       if target:
           public_version = target.get_viewable()
           if public_version and hasattr(public_version.aq_inner, 'fulltext'):
               return public_version.fulltext()
       return ""

    security.declareProtected(SilvaPermissions.View, 'get_link_status')
    def get_link_status(self, content=None):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        if content is None:
            content = self.get_haunted_unrestricted(check=0)
        if self._content_path is None:
            return self.LINK_EMPTY
        if content is None:
            return self.LINK_VOID
        if IContainer.providedBy(content):
            return self.LINK_FOLDER
        if not IContent.providedBy(content):
            return self.LINK_NO_CONTENT
        if IGhost.providedBy(content):
            return self.LINK_GHOST
        return self.LINK_OK


class GhostView(silvaviews.View):
    grok.context(IGhostContent)

    broken_message = _(u"This 'ghost' document is broken. "
                       u"Please inform the site administrator.")

    def render(self):
        # FIXME what if we get circular ghosts?
        self.request.other['ghost_model'] = aq_inner(self.context)
        try:
            content = self.content.get_haunted_unrestricted()
            if content is None:
                return self.broken_message
            if content.get_viewable() is None:
                return self.broken_message
            permission = self.is_preview and 'Read Silva content' or 'View'
            if getSecurityManager().checkPermission(permission, content):
                return content.view()
            raise Unauthorized(
                u"You does not have the permission to "
                u"see the target of this ghost")
        finally:
            del self.request.other['ghost_model']


def ghostFactory(container, id, haunted_object):
    """add new ghost to container

        container: container to add ghost to (must be acquisition wrapped)
        id: (str) id for new ghost in container
        haunted_object: object to be haunted (ghosted), acquisition wrapped
        returns created ghost

        actual ghost created depends on haunted object
        on IContainer a GhostFolder is created
        on IVersionedContent a Ghost is created
    """
    addProduct = container.manage_addProduct['Silva']
    content_url = '/'.join(haunted_object.getPhysicalPath())
    if IContainer.providedBy(haunted_object):
        factory = addProduct.manage_addGhostFolder
    elif IContent.providedBy(haunted_object):
        if haunted_object.meta_type == 'Silva Ghost':
            version = getLastVersionFromGhost(haunted_object)
            content_url = version.get_haunted_url()
        factory = addProduct.manage_addGhost
    factory(id, haunted_url=content_url)
    ghost = getattr(container, id)
    return ghost


def canBeHaunted(to_be_haunted):
    if IGhost.providedBy(to_be_haunted):
        return 0
    if (IContainer.providedBy(to_be_haunted) or
            IContent.providedBy(to_be_haunted)):
        return 1
    return 0


