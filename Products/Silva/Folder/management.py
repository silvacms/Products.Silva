# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import re

from five import grok
from zope.cachedescriptors.property import Lazy
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.lifecycleevent import ObjectCopiedEvent
from zope.lifecycleevent import ObjectMovedEvent
from zope.lifecycleevent import ObjectRemovedEvent

from Acquisition import aq_parent, aq_inner, aq_base
from OFS.CopySupport import sanity_check as move_check
from OFS.event import ObjectWillBeMovedEvent
from OFS.event import ObjectWillBeRemovedEvent
from OFS.event import ObjectClonedEvent
from OFS.subscribers import compatibilityCall

from Products.Silva import helpers
from Products.Silva.Ghost import get_ghost_factory

from infrae.comethods import cofunction
from silva.core import conf as silvaconf
from silva.core.interfaces import IContainerManager
from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IContainer
from silva.core.interfaces import ContainerError, ContentError
from silva.core.interfaces import ISilvaNameChooser
from silva.translations import translate as _


class ContainerManager(grok.Adapter):
    grok.context(IContainer)
    grok.implements(IContainerManager)
    grok.provides(IContainerManager)

    def __make_id(self, type, identifier):
        # Create a new identifier that is unused in the container.
        count = 0
        match = re.match('^' + type + '([0-9]*)_of_(.*)', identifier)
        if match:
            count = int(match.group(1) or '1')
            identifier = match.group(2)
        candidate = identifier
        while self.context._getOb(candidate, None) is not None:
            candidate = type + '%s_of_%s' % (
                count and count + 1 or '', identifier)
            count += 1
        return candidate

    def __copy(self, content, to_identifier):
        # Copy a content to to_identifier in the container
        copy = content._getCopy(self.context)
        copy._setId(to_identifier)
        notify(ObjectCopiedEvent(copy, content))

        self.context._setObject(to_identifier, copy)
        copy = self.context._getOb(to_identifier)

        compatibilityCall('manage_afterClone', copy, copy)
        notify(ObjectClonedEvent(copy))
        return copy

    def __move(self, content, from_container, from_identifier, to_identifier):
        # Move a content into the container
        notify(ObjectWillBeMovedEvent(
                content,
                 from_container, from_identifier,
                 self.context, to_identifier))

        from_container._delObject(
            from_identifier, suppress_events=True)

        content = aq_base(content)
        content._setId(to_identifier)

        self.context._setObject(
            to_identifier, content, set_owner=0, suppress_events=True)

        content = self.context._getOb(to_identifier)

        notify(ObjectMovedEvent(
                content,
                from_container, from_identifier,
                self.context, to_identifier))
        return content

    @Lazy
    def __addables(self):
        return set(IAddableContents(self.context).get_authorized_addables())

    def __verify_copyable(self, content):
        if not content.cb_isCopyable():
            return ContainerError(
                _(u"You are unauthorized to copy this content."),
                content)
        if content.meta_type not in self.__addables:
            return ContainerError(
                _(u"You cannot add this content type in this container."),
                content)
        return None

    def __verify_moveable(self, content):
        try:
            content.is_deletable()
        except ContentError as error:
            return error
        if not content.cb_isMoveable():
            return ContainerError(
                _(u"You are unauthorized to move this content."),
                content)
        if not  move_check(self.context, content):
            return ContainerError(
                _(u"You cannot move this content to this container."),
                content)
        if content.meta_type not in self.__addables:
            return ContainerError(
                _(u"You cannot add this content type in this container."),
                content)
        return None

    @silvaconf.protect('silva.ChangeSilvaContent')
    @cofunction
    def copier(self):

        def make_copy(content):
            identifier = self.__make_id('copy', content.getId())
            copy = self.__copy(content, identifier)

            # Close, maybe should be in a event
            helpers.unapprove_close_helper(copy)
            return copy

        content = yield
        while content is not None:
            result = self.__verify_copyable(content)
            if result is None:
                result = make_copy(content)
            content = yield result

    @silvaconf.protect('silva.ChangeSilvaContent')
    @cofunction
    def mover(self):
        any_moves = False

        def do_move(from_container, content):
            from_identifier = content.getId()
            to_identifier = self.__make_id('move', from_identifier)

            content = self.__move(
                content, from_container, from_identifier, to_identifier)

            content.manage_changeOwnershipType(explicit=0)

            notifyContainerModified(from_container)
            return content

        content = yield
        while content is not None:
            result = self.__verify_moveable(content)
            if result is None:
                from_container = aq_parent(aq_inner(content))
                if (aq_base(from_container) is not aq_base(self.context)):
                    result = do_move(from_container, content)
                    any_moves = True
                else:
                    result = ContainerError(
                        _(u"Content already in the target container."),
                        content)

            content = yield result

        if any_moves:
            notifyContainerModified(self.context)

    @silvaconf.protect('silva.ChangeSilvaContent')
    @cofunction
    def renamer(self):
        any_renames = False

        data = yield
        while data is not None:
            content, to_identifier, to_title = data
            result = None

            # Rename identifier
            from_identifier = content.getId()
            if to_identifier is not None and from_identifier != to_identifier:
                result = self.__verify_moveable(content)
                if result is None:
                    try:
                        ISilvaNameChooser(self.context).checkName(
                            to_identifier, content)
                    except ContentError as e:
                        result = ContainerError(reason=e.reason,
                                content=content)
                if result is None:
                    content = self.__move(
                        content, self.context, from_identifier, to_identifier)
                    any_renames = True

            # Update title
            if to_title is not None:
                if not isinstance(to_title, unicode):
                    to_title = to_title.decode('utf-8')
                editable = content.get_editable()
                if editable is None:
                    if result is None:
                        result = ContentError(
                            _(u"There is no editable version to set the title on."),
                            content)
                elif editable.get_title() != to_title:
                    try:
                        editable.set_title(to_title)
                    except ContentError as error:
                        result = error

            if result is None:
                result = content

            data = yield result

        if any_renames:
            notifyContainerModified(self.context)

    @silvaconf.protect('silva.ChangeSilvaContent')
    @cofunction
    def ghoster(self):
        content = yield
        while content is not None:
            result = self.__verify_copyable(content)
            if result is None:
                factory = get_ghost_factory(self.context, content)
                if factory is None:
                    identifier = self.__make_id('copy', content.getId())
                    result = self.__copy(content, identifier)
                else:
                    identifier = self.__make_id('ghost', content.getId())
                    try:
                        result = factory(identifier)
                    except ContentError as result:
                        pass

            content = yield result

    @silvaconf.protect('silva.ChangeSilvaContent')
    @cofunction
    def deleter(self):
        to_delete = []
        container_ids = set(self.context.objectIds())

        try:
            protected = self.context._reserved_names
        except:
            protected = ()

        content = yield
        while content is not None:
            try:
                content.is_deletable()
            except ContentError as error:
                result = error
            else:
                content_id = content.getId()
                if (content_id in container_ids and
                    content_id not in protected and
                    aq_base(self.context) is aq_base(aq_parent(content))):
                    to_delete.append((content_id, content))
                    result = content
                else:
                    result = ContentError(
                        _(u"Cannot delete content."),
                        content)
            content = yield result

        # Event
        for identifier, content in to_delete:
            compatibilityCall('manage_beforeDelete', content, content, self.context)
            notify(ObjectWillBeRemovedEvent(content, self.context, identifier))

        # Delete
        for identifier, content in to_delete:
            self.context._objects = tuple(
                [i for i in self.context._objects if i['id'] != identifier])
            self.context._delOb(identifier)
            try:
                content._v__object_deleted__ = 1
            except:
                pass

        # Event
        for identifier, content in to_delete:
            notify(ObjectRemovedEvent(content, self.context, identifier))

        if to_delete:
            notifyContainerModified(self.context)
