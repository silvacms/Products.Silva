# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from zope import interface

# Python
from bisect import insort_right

# zope
try:
    from App.class_init import InitializeClass # Zope 2.12
except ImportError:
    from Globals import InitializeClass # Zope < 2.12

from AccessControl import ClassSecurityInfo
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# silva
from silva.core.interfaces import IContainerPolicy
from silva.core.interfaces import IInvisibleService
from silva.core.services.base import SilvaService

from silva.core import conf as silvaconf

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

class ContainerPolicyRegistry(SilvaService):

    security = ClassSecurityInfo()
    id = 'service_containerpolicy'
    title = 'Container Policies Listing'
    interface.implements(IInvisibleService)
    meta_type = 'Silva Container Policy Registry'

    manage_options = (
        {'label': 'Edit', 'action': 'manage_main'},
        ) + SilvaService.manage_options

    security.declareProtected('View management screens', 'manage_main')
    manage_main = PageTemplateFile('www/containerPolicyEdit.zpt', globals())

    silvaconf.icon('www/containerpolicy_service.png')
    silvaconf.factory('manage_addContainerPolicyRegistry')

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

    def listAddablePolicies(self, model):
        """return a formulator items list of policies available
        in the current context"""
        allowed_addables = model.get_silva_addables_allowed()
        return [ (p,p) for p in self.listPolicies()
                 if p in allowed_addables or p == 'None']
    
    def register(self, name, policy, priority=0.0):
        """register policy
        If policy is simple and is a factory for a silva content type, 'name'
        should be the silva conte type's meta_type.  This is required to hide
        policies which create addables not allowed in the publication.
        Policy should be the container policy class."""
        msg = ('The object %(policy)s does not implement IContainerPolicy, '
                    'try restarting Zope.')
        msg = msg % {'policy': repr(policy)}
        assert IContainerPolicy.implementedBy(policy), msg
        self._policies[name] = (policy(), priority)
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

class NothingPolicy(Persistent):

    implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        pass
