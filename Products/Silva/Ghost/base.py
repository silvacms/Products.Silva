# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope 3
from five import grok
from zeam.component import getComponent
from zope.component import getUtility

# Zope 2
from Acquisition import aq_inner
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva import SilvaPermissions

from silva.core.interfaces import errors
from silva.core.interfaces.errors import ContentError
from silva.core.interfaces import IGhostAware, IGhostManager, IPublishable
from silva.core.references.reference import DeleteSourceReferenceValue
from silva.core.references.reference import WeakReferenceValue
from silva.core.references.interfaces import IReferenceService
from silva.translations import translate as _


class GhostBaseManipulator(object):

    def __init__(self, manager, target, identifier):
        self.manager = manager
        self.target = target
        self.identifier = identifier
        self.__references = []

    def save_references_of(self, content):
        service = getUtility(IReferenceService)
        self.__references = []
        for reference in list(service.get_references_to(content)):
            # Break the reference so we can replace it.
            reference.set_target_id(0)
            self.__references.append(reference)

    def restore_references_to(self, content):
        for reference in self.__references:
            reference.set_target(content)

    def create(self, recursive=False):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def need_update(self):
        raise NotImplementedError

    def delete(self):
        assert self.manager.ghost is not None
        self.manager.container.manage_delObjects([self.identifier])
        self.manager.ghost = None
        return None

    def recreate(self):
        # Recreate the ghost, conserving the references.
        assert self.manager.ghost is not None
        self.save_references_of(self.manager.ghost)
        self.delete()
        self.create()
        self.restore_references_to(self.manager.ghost)

    def verify(self, recursive=False):
        if self.manager.ghost is None:
            if self.target is not None:
                return self.create(recursive=recursive)
        elif self.need_update():
            return self.update()
        return self.manager.ghost


class GhostBaseManager(object):
    grok.implements(IGhostManager)
    manipulator = GhostBaseManipulator

    def __init__(self, ghost=None, container=None,
                 auto_delete=False, auto_publish=False):
        self.ghost = ghost
        if container is None:
            assert ghost is not None, 'Need to provide ghost or a container'
            container = ghost.get_container()
        self.container = container
        self.auto_delete = auto_delete
        self.auto_publish = auto_publish

    def modify(self, target, identifier=None):
        if identifier is None:
            identifier = target.getId()
        if IGhostAware.providedBy(target):
            target = target.get_haunted()
        return self.manipulator(self, target, identifier)

    def validate(self, target, adding=False):
        if target is None:
            return errors.EmptyInvalidTarget()
        if IGhostAware.providedBy(target):
            return errors.GhostInvalidTarget()
        # Check for cicular reference. You cannot select an ancestor
        # or descandant of the ghost (or the ghost)
        target_path = target.getPhysicalPath()
        if adding:
            test_path = self.container.getPhysicalPath()
        else:
            test_path = self.ghost.getPhysicalPath()

        # XXX !!!!
        if not adding and len(target_path) > len(test_path):
            if test_path == target_path[:len(test_path)]:
                return errors.CircularInvalidTarget()
        elif target_path == test_path[:len(target_path)]:
                return errors.CircularInvalidTarget()


class GhostBase(object):
    """baseclass for Ghosts (or Ghost versions if it's versioned)
    """
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_title')
    def set_title(self, title):
        """You cannot change the title of a ghost.
        """
        if title is not None:
            raise ContentError(
                _(u"A ghost title is immutable."),
                self.get_silva_object())

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title')
    def get_title(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is not None:
            if not IPublishable.providedBy(content) or content.is_published():
                return content.get_title()
        return _(u"Ghost target is broken")

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title')
    def get_short_title(self):
        """Get short title.
        """
        content = self.get_haunted()
        if content is not None:
            if not IPublishable.providedBy(content) or content.is_published():
                return content.get_short_title()
        return _(u"Ghost target is broken")

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_title_editable')
    def get_title_editable(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is not None:
            return content.get_title_editable()
        return _(u"Ghost target is broken")

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_short_title_editable')
    def get_short_title_editable(self):
        """Get title.
        """
        content = self.get_haunted()
        if content is not None:
            return content.get_short_title_editable()
        return _(u"Ghost target is broken")

    def _get_haunted_factories(self, auto_delete=False):
        # Give the possibilties to override the selection of reference
        # factories.
        if auto_delete:
            return DeleteSourceReferenceValue
        return WeakReferenceValue

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_haunted')
    def set_haunted(self, content, auto_delete=False):
        """ Set the content as the haunted object
        """
        service = getUtility(IReferenceService)
        factory = self._get_haunted_factories(auto_delete)
        reference = service.get_reference(
            aq_inner(self), name=u"haunted", add=True, factory=factory)
        if isinstance(content, int):
            reference.set_target_id(content)
        else:
            reference.set_target(content)

    security.declareProtected(SilvaPermissions.View, 'get_haunted')
    def get_haunted(self):
        service = getUtility(IReferenceService)
        reference = service.get_reference(aq_inner(self), name=u"haunted")
        if reference is not None:
            return reference.target
        return None

    security.declareProtected(SilvaPermissions.View, 'get_link_status')
    def get_link_status(self):
        """Return an error code if this version of the ghost is broken.
        returning None means the ghost is Ok.
        """
        ghost = self.get_silva_object()
        get_manager = getComponent((ghost,), IGhostManager)
        return get_manager(ghost=ghost).validate(self.get_haunted())


InitializeClass(GhostBase)
