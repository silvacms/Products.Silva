# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
from bisect import insort_right

# Zope
from five import grok
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Persistence import Persistent

# Silva
from silva.core import conf as silvaconf
from silva.core.interfaces import IContainerPolicy, IAddableContents
from silva.core.services.interfaces import IContainerPolicyService
from silva.core.services.base import SilvaService


class _Policy:
    def __init__(self, name, priority):
        self._name = name
        self._priority = priority

    def __cmp__(self, other):
        sort = cmp(self._priority, other._priority)
        if sort == 0:
            sort = cmp(self._name, other._name)
        return sort


class ContainerPolicyRegistry(SilvaService):
    meta_type = 'Silva Container Policy Registry'
    grok.implements(IContainerPolicyService)
    grok.name('service_containerpolicy')
    silvaconf.default_service()

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        super(ContainerPolicyRegistry, self).__init__(*args, **kwargs)
        self.__policies = {}
        self.register('None', NothingPolicy, 100)

    security.declareProtected(
        'Access contents information', 'get_policy')
    def get_policy(self, name):
        return self.__policies[name][0]

    security.declareProtected(
        'Access contents information', 'list_policies')
    def list_policies(self):
        sorted_policies = []
        for key, value in self.__policies.items():
            insort_right(sorted_policies, _Policy(key, value[1]))
        return [p._name for p in sorted_policies]

    security.declareProtected(
        'Access contents information', 'list_addable_policies')
    def list_addable_policies(self, content):
        allowed_addables = IAddableContents(content).get_authorized_addables()
        return [p for p in self.list_policies()
                if p in allowed_addables or p == 'None']

    security.declareProtected(
        'View management screens', 'register')
    def register(self, name, policy, priority=0.0):
        """Register policy.
        """
        assert IContainerPolicy.implementedBy(policy)
        self.__policies[name] = (policy(), priority)
        self._p_changed = 1

    security.declareProtected(
        'View management screens', 'unregister')
    def unregister(self, name):
        """Unregister policy.
        """
        try:
            del self.__policies[name]
        except KeyError:
            pass
        self._p_changed = 1


InitializeClass(ContainerPolicyRegistry)


class NothingPolicy(Persistent):
    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        pass
