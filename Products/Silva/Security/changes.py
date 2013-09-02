# -*- coding: utf-8 -*-
# Copyright (c) 2013 Infrae. All rights reserved.
# See also LICENSE.txt


from AccessControl import getSecurityManager
from DateTime import DateTime

from five import grok
from silva.core.interfaces import IUpgradeTransaction
from silva.core.services.delayed import Task
from silva.core.services.interfaces import IMemberService, IMetadataService
from zope.component import queryUtility


class Key(object):
    __slots__ = ('content', 'hash')

    def __init__(self, content):
        self.content = content
        self.hash = hash((content._p_oid, content._p_jar._db.database_name))

    def __eq__(self, other):
        return other.content == self.content

    def __hash__(self):
        return self.hash


class ChangesTask(Task):
    """Task in charge of updating the modification date and last
    author in Silva.

    Of course this assume that all the transaction is executed by the
    same author, that is the case in Zope.
    """
    priority = 0                # It must be one of the first things to be done.

    def __init__(self, enabled=True, changes=None):
        self._enabled = enabled
        self._changes = {} if changes is None else changes.copy()

    def copy(self):
        return ChangesTask(self._enabled, self._changes)

    def disable(self):
        # We want to disable this feature during upgrade.
        self._enabled = False

    def modified(self, content, created=False):
        # Content have been modified.
        if self._enabled:
            key = Key(content)
            if created or key not in self._changes:
                self._changes[key] = created

    def finish(self):
        if not self._enabled or not self._changes:
            # Don't do things.
            pass

        members = queryUtility(IMemberService)
        if members is None:
            return
        now = DateTime()
        login = getSecurityManager().getUser().getId()
        metadata = queryUtility(IMetadataService)

        for change, created in self._changes.iteritems():
            # Update author
            # XXX This could probably be done outside of the loop
            user = members.get_cached_member(login, location=change.content)
            change.content.set_last_author_info(user)

            if metadata is not None:
                # Update metadata
                binding = metadata.getMetadata(change.content)
                if binding is None or binding.read_only:
                    continue
                values = {'modificationtime': now}
                if created:
                    values['creationtime'] = now
                binding.setValues('silva-extra', values)


@grok.subscribe(IUpgradeTransaction)
def disable_upgrade(event):
    ChangesTask.get().disable()
