# -*- coding: utf-8 -*-
# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 3
from five import grok
from zope.interface import Interface

# Zope 2
from Acquisition import aq_inner, aq_base
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from zExceptions import Unauthorized

# Silva
from Products.Silva.VersionedContent import CatalogedVersionedContent
from Products.Silva.Version import CatalogedVersion
from Products.Silva import SilvaPermissions

from zeam.form.base import FAILURE
from zeam.form.base.actions import Action, Actions
from zeam.form.base.fields import Fields
from zeam.form.silva.form import SMIAddForm
from zeam.form.silva.form import SMIEditForm
from zeam.form.silva.actions import CancelAddAction, CancelEditAction

# this initializes the widgets
import silva.core.references.widgets.zeamform

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import (
    IContainer, IContent, IGhost, IGhostFolder, IGhostContent, IGhostVersion)
from silva.translations import translate as _

from silva.core.references.reference import ReferenceProperty
from silva.core.conf import schema as silvaschema
from silva.core.references.reference import Reference


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

    _haunted = ReferenceProperty(name=u'haunted')

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
        content = self.get_haunted()
        if content is None:
            return ("Ghost target is broken")
        else:
            return content.get_title()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_editable')
    def get_title_editable(self):
        """Get title.
        """
        content = self.get_haunted()
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
        content = self.get_haunted()
        if content is None:
            return ("Ghost target is broken")
        else:
            short_title = content.get_short_title()
        if not short_title:
            return self.get_title()
        return short_title
    # /those should go away

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted')
    def set_haunted(self, content):
        """ Set the content as the haunted object
        """
        self._haunted = content

    security.declareProtected(SilvaPermissions.View, 'get_haunted')
    def get_haunted(self):
        return self._haunted

    security.declareProtected(SilvaPermissions.View, 'get_haunted_url')
    def get_haunted_url(self):
        """Get content url.
        """
        if self._haunted is None:
            return None
        return "/".join(self._haunted.getPhysicalPath())

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'haunted_path')
    def haunted_path(self):
        return self._haunted.getPhysicalPath()

    security.declareProtected(SilvaPermissions.View,'get_link_status')
    def get_link_status(self):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        raise NotImplementedError, "implemented in subclasses"


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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_title_editable')
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

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_haunted_url')
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
        haunted = public.get_haunted()
        if haunted is None:
            return False
        return haunted.is_published()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_modification_datetime')
    def get_modification_datetime(self, update_status=1):
        """Return modification datetime."""
        super_method = Ghost.inheritedAttribute(
            'get_modification_datetime')
        content = self.getLastVersion().get_haunted()

        if content is not None:
            return content.get_modification_datetime(update_status)
        else:
            return super_method(self, update_status)


InitializeClass(Ghost)


class GhostVersion(GhostBase, CatalogedVersion):
    """Ghost version.
    """
    meta_type = 'Silva Ghost Version'
    grok.implements(IGhostVersion)

    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
       target = self.get_haunted()
       if target:
           public_version = target.get_viewable()
           if public_version and hasattr(aq_base(public_version), 'fulltext'):
               return public_version.fulltext()
       return ""

    security.declareProtected(SilvaPermissions.View, 'get_link_status')
    def get_link_status(self):
        """return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        content = self._haunted
        if content is None:
            return self.LINK_EMPTY
        if IContainer.providedBy(content):
            return self.LINK_FOLDER
        if not IContent.providedBy(content):
            return self.LINK_NO_CONTENT
        if IGhost.providedBy(content):
            return self.LINK_GHOST
        return self.LINK_OK


class IGhostSchema(Interface):
    id = silvaschema.ID(
        title=_(u"id"),
        description=_(u"No spaces or special characters besides ‘_’ or ‘-’ or ‘.’"),
        required=True)

    haunted = Reference(IContent,
            title=_(u"target"),
            description=_(u"The silva object the ghost is mirroring"),
            required=True)


class AddAction(Action):

    def add(self, parent, data, form):
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addGhost(
            data['id'], 'Ghost', haunted=data['haunted'])

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            return FAILURE
        content = self.add(form.context, data , form)
        return form.redirect(self.next_url(form, content, form.context))

    def next_url(self, form, content, parent):
        return "%s/edit" % parent.absolute_url()


class AddAndEdit(AddAction):

    def next_url(self, form, content, parent):
        return "%s/edit" % content.absolute_url()


class GhostAddForm(SMIAddForm):
    """Add form for a ghost
    """
    grok.name(u"Silva Ghost")
    grok.context(IGhost)

    fields = Fields(IGhostSchema)
    description = Ghost.__doc__
    actions = Actions(CancelAddAction(_(u'cancel')),
                      AddAction(_(u'save')),
                      AddAndEdit(_(u'save + edit'),
                                 identifier="save_edit"))


class GhostEditForm(SMIEditForm):
    """ Edit form for Ghost
    """
    grok.context(IGhost)
    fields = Fields(IGhostSchema).omit('id')


class GhostView(silvaviews.View):
    grok.context(IGhostContent)

    broken_message = _(u"This 'ghost' document is broken. "
                       u"Please inform the site administrator.")

    def render(self):
        # FIXME what if we get circular ghosts?
        self.request.other['ghost_model'] = aq_inner(self.context)
        try:
            content = self.content.get_haunted()
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
            target = target.get_hauted()
        factory = factory.manage_addGhostFolder
    elif IContent.providedBy(target):
        if IGhostContent.providedBy(target):
            target = target.getLastVersion().get_haunted()
        factory = factory.manage_addGhost
    factory(identifier, None, haunted=target)
    return getattr(container, identifier)



