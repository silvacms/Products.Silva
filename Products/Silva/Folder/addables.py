# -*- coding: utf-8 -*-
# Copyright (c) 2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from five import grok

from Products.Silva.ExtensionRegistry import extensionRegistry
from AccessControl import getSecurityManager
from Acquisition import aq_parent

from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IRoot, ISilvaObject, IFolder


class AddableContents(grok.Adapter):
    grok.context(IFolder)
    grok.implements(IAddableContents)
    grok.provides(IAddableContents)

    def __init__(self, context):
        self.context = context
        self.root = context.get_root()
        self._is_forbidden = self.root.is_silva_addable_forbidden

    def get_authorized_addables(self):
        check_permission = getSecurityManager().checkPermission
        can_add = lambda name: check_permission('Add %ss' % name, self.context)

        return filter(can_add, self.get_container_addables())

    def get_container_addables(self):
        all_addables = self.get_all_addables()

        # Check for restriction on the container
        locally_addables = self._get_locally_addables()
        if locally_addables is not None:
            is_locally_addable = lambda name: name in locally_addables
            return filter(is_locally_addable, all_addables)

        return all_addables

    def get_all_addables(self):
        return map(operator.itemgetter('name'),
                   filter(self._is_addable, extensionRegistry.get_addables()))

    def _get_locally_addables(self):
        container = self.context
        while IFolder.providedBy(container):
            addables = container.get_silva_addables_allowed_in_container()
            if addables is not None:
                return addables
            container = aq_parent(container)
        return None

    def _is_addable(self, addable):
        if 'instance' in addable:
            if not ISilvaObject.implementedBy(addable['instance']):
                return False
            if IRoot.implementedBy(addable['instance']):
                return False

            return (
                not self._is_forbidden(addable['name']) and
                extensionRegistry.is_installed(addable['product'], self.root))

        return False
