# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.8.6.1.16.1 $
# Python
from bisect import insort_right

# zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# silva
from Products.Silva import SilvaPermissions
from Products.Silva.interfaces import IContainerPolicy, IContainer

# XXX: can these "helper" classes for ordering be refactored in something
# more generic? See also ExtensionRegistry.Addable.
class _Policy:
    def __init__(self, name, priority):
        self._name = name
        self._priority = priority
        
    def __cmp__(self, other):
        sort = cmp(self._priority, other._priority)
        if sort == 0:
            sort = cmp(self._name, other._name)
        return sort

class ContainerPolicyRegistry(SimpleItem):

    security = ClassSecurityInfo()
    id = 'service_containerpolicy'
    meta_type = 'Silva Container Policy Registry'

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
        ) + SimpleItem.manage_options

    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/containerPolicyEdit.zpt', globals())

    def __init__(self):
        self._policies = {}
    
    def getPolicy(self, name):
        """return policy of given name

            raises KeyError if policy doesn't exist
        """
        return self._policies[name][0]
    
    def listPolicies(self):
        sorted_policies = []
        for key, value in self._policies.items():
            insort_right(sorted_policies, _Policy(key, value[1]))
        return [p._name for p in sorted_policies]
    
    def register(self, name, policy, priority=0.0):
        """register policy"""
        assert IContainerPolicy.isImplementedBy(policy), "The object %r " \
            "does not implement IContainerPolicy, try restarting Zope." % (
                policy, )
        self._policies[name] = (policy, priority)
        self._p_changed = 1

    def unregister(self, name):
        """unregister policy"""
        try:
            del(self._policies[name])
        except KeyError:
            pass
        self._p_changed = 1
        
InitializeClass(ContainerPolicyRegistry)

def manage_addContainerPolicyRegistry(dispatcher):
    cpr = ContainerPolicyRegistry()
    dispatcher._setObject(cpr.id, cpr)
    return ''

class _NothingPolicy(Persistent):

    __implements__ = IContainerPolicy

    def createDefaultDocument(self, container, title):
        pass
        
NothingPolicy = _NothingPolicy()
    
