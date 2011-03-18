# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

from five import grok
from zope.cachedescriptors.property import CachedProperty
from zope.lifecycleevent import ObjectCopiedEvent
from zope.container.contained import notifyContainerModified
from zope.event import notify
from zope.lifecycleevent import ObjectRemovedEvent
from zope.lifecycleevent import ObjectMovedEvent

from Acquisition import aq_parent, aq_inner, aq_base
from OFS.CopySupport import sanity_check as move_check
from OFS.event import ObjectWillBeMovedEvent
from OFS.event import ObjectWillBeRemovedEvent
from OFS.event import ObjectClonedEvent
from OFS.subscribers import compatibilityCall

from Products.Silva import helpers, mangle
from Products.Silva.Ghost import ghost_factory

from silva.core.interfaces import IContainerManager, IAddableContents
from silva.core.interfaces import IContainer, IAsset


def comethod(func):

    class wrapper(object):

        def __init__(self, iterator):
            self.__iterator = iterator
            self.__iterator.send(None)
            self.__done = False

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None and not self.__done:
                self.finish()

        def add(self, value):
            return self.__iterator.send(value)

        def finish(self):
            try:
                self.__iterator.send(None)
            except StopIteration:
                self.__done = True
                return True
            return False

    def wrapped(*args):
        return wrapper(func(*args))

    return wrapped


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

    def __move(self, content, from_container, from_identifier, to_identifier):
        # Move a content into the container
        notify(ObjectWillBeMovedEvent(
                content,
                 from_container, from_identifier,
                 self.context, to_identifier))

        self.context._delObject(
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

    @CachedProperty
    def __addables(self):
        return set(IAddableContents(self.context).get_authorized_addables())

    def __is_copyable(self, content):
        return (content.cb_isCopyable() and
                content.meta_type in self.__addables)

    def __is_moveable(self, content):
        return (content.is_deletable() and
                content.cb_isMoveable() and
                move_check(self.context, content) and
                content.meta_type in self.__addables)

    @comethod
    def copier(self):

        def make_copy(content):
            identifier = self.__make_id('copy', content.getId())
            copy = self.__copy(content, identifier)

            # Close, maybe should be in a event
            helpers.unapprove_close_helper(copy)
            return copy

        content = yield
        while content is not None:
            result = False, None
            if self.__is_copyable(content):
                result = True, make_copy(content)
            content = yield result

    @comethod
    def mover(self):
        any_moves = False

        def do_move(from_container, content):
            from_identifier = content.getId()
            to_identifier = self.__make_id('move', from_identifier)

            content = self.__move(
                content, from_container, from_identifier, to_identifier)

            content.manage_changeOwnershipType(explicit=0)

            # Close, maybe should be in a event
            helpers.unapprove_close_helper(content)

            notifyContainerModified(from_container)
            return content

        content = yield
        while content is not None:
            result = False, None
            if self.__is_moveable(content):
                from_container = aq_parent(aq_inner(content))
                if (aq_base(from_container) is not aq_base(self.context)):
                    result = True, do_move(from_container, content)
                    any_moves = True
            content = yield result

        if any_moves:
            notifyContainerModified(self.context)

    @comethod
    def renamer(self):
        any_renames = False

        data = yield
        while data is not None:
            content, to_identifier, to_title = data
            result = None

            # Rename identifier
            from_identifier = content.getId()
            if (from_identifier != to_identifier and
                self.__is_moveable(content) and
                mangle.Id(self.context, to_identifier, instance=content).isValid()):

                try:
                    order = self.context._ordered_ids.index(from_identifier)
                except ValueError:
                    order = None

                content = self.__move(
                    content, self.context, from_identifier, to_identifier)
                if order is not None:
                    self.context.move_to([to_identifier], order)
                result = content
                any_renames = True

            # Update title
            if content.get_title() != to_title:
                content.set_title(to_title)
                result = content

            data = yield result

        if any_renames:
            notifyContainerModified(self.context)

    @comethod
    def ghoster(self):
        content = yield
        while content is not None:
            result = False, None
            if self.__is_copyable(content):
                if IAsset.providedBy(content):
                    identifier = self.__make_id('copy', content.getId())
                    result = self.__copy(content, identifier)
                else:
                    identifier = self.__make_id('ghost', content.getId())
                    result = ghost_factory(self.context, identifier, content)

            content = yield result

    @comethod
    def deleter(self):
        to_delete = []
        container_ids = set(self.context.objectIds())

        try:
            protected = self.context._reserved_names
        except:
            protected = ()

        content = yield
        while content is not None:
            status = False
            if content.is_deletable():
                content_id = content.getId()
                if content_id in container_ids and content_id not in protected:
                    to_delete.append((content_id, content))
                    status = True
            content = yield status

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
