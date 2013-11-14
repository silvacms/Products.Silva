# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zeam.component import component

# Zope 2
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.interfaces.errors import ContentInvalidTarget, ContentError
from silva.core.interfaces import IContent, IGhost, IGhostVersion
from silva.core.interfaces import IPublicationWorkflow, IGhostManager
from silva.translations import translate as _

from .base import GhostBase, GhostBaseManipulator, GhostBaseManager


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


InitializeClass(GhostVersion)


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
    silvaconf.icon('icons/ghost.png')
    silvaconf.version_class(GhostVersion)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_haunted')
    def get_haunted(self):
        version = self.get_previewable()
        if version is not None:
            return version.get_haunted()
        return None

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
        version = self.get_viewable()
        if version is not None:
            content = version.get_haunted()
            if content is not None:
                return content.get_modification_datetime()
        return super(Ghost, self).get_modification_datetime()

InitializeClass(Ghost)


class GhostManipulator(GhostBaseManipulator):

    def create(self, recursive=False):
        assert self.manager.ghost is None
        ghost = None
        factory = self.manager.container.manage_addProduct['Silva']
        try:
            factory.manage_addGhost(self.identifier, None)
        except ValueError as error:
            raise ContentError(error[0], content=self.target)
        ghost = self.manager.container._getOb(self.identifier)
        version = ghost.get_editable()
        version.set_haunted(
            self.target, auto_delete=self.manager.auto_delete)
        if self.manager.auto_publish:
            IPublicationWorkflow(ghost).publish()
        self.manager.ghost = ghost
        return ghost

    def update(self):
        assert self.manager.ghost is not None
        if IGhost.providedBy(self.manager.ghost):
            publication = IPublicationWorkflow(self.manager.ghost)
            if self.manager.ghost.get_editable() is None:
                publication.new_version()
            version = self.manager.ghost.get_editable()
            version.set_haunted(
                self.target, auto_delete=self.manager.auto_delete)
            if self.manager.auto_publish:
                publication.publish()
        else:
            self.recreate()
        return self.manager.ghost

    def need_update(self):
        if IGhost.providedBy(self.manager.ghost):
            viewable = self.manager.ghost.get_viewable()
            return self.target != viewable.get_haunted()
        return IContent.providedBy(self.manager.ghost)


@component(IContent, provides=IGhostManager)
class GhostManager(GhostBaseManager):
    manipulator = GhostManipulator

    def validate(self, target, adding=False):
        error = super(GhostManager, self).validate(target, adding)
        if error is None:
            if not IContent.providedBy(target):
                return ContentInvalidTarget()
        return error
