# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.component import getUtility

# Zope 2
from Acquisition import aq_inner, aq_base
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from zExceptions import Unauthorized

# Silva
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import SilvaPermissions

from zeam.form import silva as silvaforms

from silva.core import conf as silvaconf
from silva.core.conf.interfaces import IIdentifiedContent
from silva.core.interfaces import (
    IContainer, IContent, IGhost, IGhostFolder, IGhostAware, IGhostVersion)
from silva.core.references.reference import Reference, get_content_id
from silva.core.references.interfaces import IReferenceService
from silva.core.views import views as silvaviews
from silva.translations import translate as _


class GhostBase(object):
    """baseclass for Ghosts (or Ghost versions if it's versioned)
    """
    security = ClassSecurityInfo()

    # status codes as returned by get_link_status
    # NOTE: LINK_FOLDER (and alike) must *only* be returned if it is an error
    # for the link to point to a folder. If it is not an error LINK_OK must
    # be returned.
    LINK_OK = None   # link is ok
    LINK_EMPTY = 1   # no link entered (XXX this cannot happen)
    LINK_FOLDER = 3  # link points to folder
    LINK_GHOST = 4   # link points to another ghost
    LINK_NO_CONTENT = 5 # link points to something which is not a content
    LINK_CONTENT = 6 # link points to content
    LINK_NO_FOLDER = 7 # link doesn't point to a folder
    LINK_CIRC = 8 # Link results in a ghost haunting itself

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_title')
    def set_title(self, title):
        """Don't do anything.
        """
        pass

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is None:
            return _(u"Ghost target is broken")
        return content.get_title()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_title_editable(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is None:
            return _(u"Ghost target is broken")
        return content.get_title_editable()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short title.
        """
        content = self.get_haunted()
        if content is None:
            return _(u"Ghost target is broken")
        return content.get_short_title()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted')
    def set_haunted(self, content):
        """ Set the content as the haunted object
        """
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u"haunted", add=True)
        if not isinstance(content, int):
            content = get_content_id(content)
        reference.set_target_id(content)

    security.declareProtected(SilvaPermissions.View, 'get_haunted')
    def get_haunted(self):
        service = getUtility(IReferenceService)
        reference = service.get_reference(
            aq_inner(self), name=u"haunted", add=True)
        return reference.target

    security.declareProtected(SilvaPermissions.View, 'get_link_status')
    def get_link_status(self):
        """Return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        haunted = self.get_haunted()
        if haunted is None:
            return self.LINK_EMPTY
        # Check for cicular reference. You cannot select an ancestor
        # or descandant of the ghost (or the ghost)
        haunted_path = haunted.getPhysicalPath()
        ghost_path = self.get_silva_object().getPhysicalPath()
        if haunted_path > ghost_path:
            if ghost_path == haunted_path[:len(ghost_path)]:
                return self.LINK_CIRC
        elif haunted_path == ghost_path[:len(haunted_path)]:
                return self.LINK_CIRC
        # Check other cases.
        if IGhostAware.providedBy(haunted):
            return self.LINK_GHOST
        if IContainer.providedBy(self):
            # If we are a container, we expect to have a container as
            # target.
            if IContent.providedBy(haunted):
                return self.LINK_CONTENT
            if not IContainer.providedBy(haunted):
                return self.LINK_NO_FOLDER
        else:
            # If we are not a container, we expect to have a content
            # as target.
            if IContainer.providedBy(haunted):
                return self.LINK_FOLDER
            if not IContent.providedBy(haunted):
                return self.LINK_NO_CONTENT
        return self.LINK_OK


class Ghost(VersionedContent):
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

    grok.implements(IGhost)
    silvaconf.icon('icons/silvaghost.gif')
    silvaconf.version_class('GhostVersion')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short_title for public use, from published version.
        """
        version = self.getLastVersion()
        return version.get_short_title()

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

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'is_published')
    def is_published(self):
        public = self.get_viewable()
        if public is None:
            return False
        haunted = public.get_haunted()
        if haunted is None:
            return False
        return haunted.is_published()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_modification_datetime')
    def get_modification_datetime(self):
        """Return modification datetime.
        """
        content = self.getLastVersion().get_haunted()

        if content is not None:
            return content.get_modification_datetime()
        return super(Ghost, self).get_modification_datetime()


InitializeClass(Ghost)


class GhostVersion(GhostBase, Version):
    """Ghost version.
    """
    meta_type = 'Silva Ghost Version'
    grok.implements(IGhostVersion)

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
       target = self.get_haunted()
       if target is not None:
           public_version = target.get_viewable()
           if public_version and hasattr(aq_base(public_version), 'fulltext'):
               return public_version.fulltext()
       return ""


class IGhostSchema(IIdentifiedContent):

    haunted = Reference(IContent,
            title=_(u"target"),
            description=_(u"The silva object the ghost is mirroring."),
            required=True)


class GhostAddForm(silvaforms.SMIAddForm):
    """Add form for a ghost
    """
    grok.name(u"Silva Ghost")
    grok.context(IGhost)

    fields = silvaforms.Fields(IGhostSchema)

    def _add(self, parent, data):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhost(
            data['id'], 'Ghost', haunted=data['haunted'])


class GhostEditForm(silvaforms.SMIEditForm):
    """ Edit form for Ghost
    """
    grok.context(IGhost)
    fields = silvaforms.Fields(IGhostSchema).omit('id')


class GhostView(silvaviews.View):
    grok.context(IGhost)

    broken_message = _(u"This 'ghost' document is broken. "
                       u"Please inform the site manager.")

    def render(self):
        content = self.content.get_haunted()
        if content is None:
            return self.broken_message
        if content.get_viewable() is None:
            return self.broken_message
        permission = self.is_preview and 'Read Silva content' or 'View'
        if getSecurityManager().checkPermission(permission, content):
            return content.view()
        raise Unauthorized(
            u"You do not have permission to "
            u"see the target of this ghost")


def ghost_factory(container, identifier, target):
    """add new ghost to container

        container: container to add ghost to (must be acquisition wrapped)
        id: (str) id for new ghost in container
        target: object to be haunted (ghosted), acquisition wrapped
        returns created ghost

        actual ghost created depends on haunted object
        on IContainer a GhostFolder is created
        on IVersionedContent a Ghost is created
    """
    factory = container.manage_addProduct['Silva']
    if IContainer.providedBy(target):
        if IGhostFolder.providedBy(target):
            target = target.get_haunted()
        factory = factory.manage_addGhostFolder
    elif IContent.providedBy(target):
        if IGhost.providedBy(target):
            target = target.getLastVersion().get_haunted()
        factory = factory.manage_addGhost
    factory(identifier, None, haunted=target)
    return container._getOb(identifier)
