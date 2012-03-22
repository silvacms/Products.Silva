# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator
from itertools import imap

from five import grok

from Products.Silva.ExtensionRegistry import extensionRegistry
from AccessControl import getSecurityManager
from Acquisition import aq_parent

from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IRoot, ISilvaObject, IFolder


def filter_contents(source, requires):
    test = lambda cls: any(imap(lambda i: i.implementedBy(cls), requires))
    return map(
        operator.itemgetter('name'),
        filter(lambda a: test(a['instance']), source))


class AddableContents(grok.Adapter):
    grok.context(IFolder)
    grok.implements(IAddableContents)
    grok.provides(IAddableContents)

    REQUIRES = [ISilvaObject]

    def __init__(self, context):
        self.context = context
        self.root = context.get_root()
        self._is_forbidden = self.root.is_silva_addable_forbidden

    def get_authorized_addables(self, require=None):
        check_permission = getSecurityManager().checkPermission
        can_add = lambda name: check_permission('Add %ss' % name, self.context)

        return filter(can_add, self.get_container_addables(require))

    def get_container_addables(self, require=None):
        all_addables = self.get_all_addables(require)

        # Check for restriction on the container
        locally_addables = self._get_locally_addables()
        if locally_addables is not None:
            is_locally_addable = lambda name: name in locally_addables
            return filter(is_locally_addable, all_addables)

        return all_addables

    def get_all_addables(self, require=None):
        if require is not None:
            if isinstance(require, (list, tuple)):
                requires = list(require)
        else:
            requires = list(self.REQUIRES)
        return filter_contents(
            filter(self._is_installed, extensionRegistry.get_addables()),
            requires)

    def _get_locally_addables(self):
        container = self.context
        while IFolder.providedBy(container):
            addables = container.get_silva_addables_allowed_in_container()
            if addables is not None:
                return addables
            container = aq_parent(container)
        return None

    def _is_installed(self, content):
        if 'instance' in content:
            if IRoot.implementedBy(content['instance']):
                return False

            return (
                not self._is_forbidden(content['name']) and
                extensionRegistry.is_installed(content['product'], self.root))

        return False
