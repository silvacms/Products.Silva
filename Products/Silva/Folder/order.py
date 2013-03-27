# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.event import notify
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.lifecycleevent.interfaces import IObjectRemovedEvent

from OFS.interfaces import IObjectWillBeMovedEvent
from OFS.interfaces import IObjectWillBeAddedEvent

from silva.core.interfaces import IOrderableContainer
from silva.core.interfaces import IOrderManager
from silva.core.interfaces import ISilvaObject, IPublishable
from silva.core.interfaces import ContentOrderChangedEvent


class OrderManager(grok.Annotation):
    grok.context(IOrderableContainer)
    grok.provides(IOrderManager)
    grok.implements(IOrderManager)

    order_only = IPublishable

    def __init__(self):
        super(OrderManager, self).__init__()
        self.order = []

    def _get_id(self, content):
        # Poor man cache.
        utility = getattr(self, '_v_utility', None)
        if utility is None:
            utility = self._v_utility = getUtility(IIntIds)
        return utility.register(content)

    def _is_valid(self, content):
        return (self.order_only.providedBy(content) and
                not (IPublishable.providedBy(content) and content.is_default()))

    def add(self, content):
        if self._is_valid(content):
            identifier = self._get_id(content)
            if identifier not in self.order:
                self.order.append(identifier)
                self._p_changed = True
                return True
        return False

    def remove(self, content):
        position = self.get_position(content)
        if position >= 0:
            del self.order[position]
            self._p_changed = True
            return True
        return False

    def move(self, content, position):
        if position >= 0 and position < len(self.order):
            old_position = self.get_position(content)
            identifier = self.order[old_position]
            if old_position >= 0:
                del self.order[old_position]
                self.order.insert(position, identifier)
                self._p_changed = True
                notify(ContentOrderChangedEvent(
                        content, position, old_position))
                return True
        return False

    def get_position(self, content):
        if not self._is_valid(content):
            return -1
        try:
            return self.order.index(self._get_id(content))
        except ValueError:
            return -1

    def __len__(self):
        return len(self.order)

    def repair(self, contents):
        # Must be called like this:
        # IObjectManager(folder).repair(folder.objectValues())
        valid_ids = set([])
        for content in contents:
            if self._is_valid(content):
                valid_ids.add(self._get_id(content))
        order = []
        seen_ids = set([])      # Check for duplicates
        changed = False
        for identifier in self.order:
            if identifier in valid_ids and identifier not in seen_ids:
                order.append(identifier)
                seen_ids.add(identifier)
            else:
                changed = True
        if changed:
            self.order = order
        return changed


@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def content_added(content, event):
    if (event.object != content or
        IObjectRemovedEvent.providedBy(event) or
        event.newParent == event.oldParent):
        return
    if IOrderableContainer.providedBy(event.newParent):
        manager = IOrderManager(event.newParent)
        manager.add(content)


@grok.subscribe(ISilvaObject, IObjectWillBeMovedEvent)
def content_removed(content, event):
    if (event.object != content or
        IObjectWillBeAddedEvent.providedBy(event) or
        event.newParent == event.oldParent):
        return
    if IOrderableContainer.providedBy(event.oldParent):
        manager = IOrderManager(event.oldParent)
        manager.remove(content)
