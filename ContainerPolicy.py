# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.3 $

# zope
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Persistence import Persistent
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# silva
from Products.Silva import SilvaPermissions
from Products.Silva.interfaces import IContainerPolicy, IContainer

class ContainerPolicyRegistry(SimpleItem):

    security = ClassSecurityInfo()
    id = 'service_containerpolicy'
    title = 'Silva ContainerPolicy Registry'


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
        return self._policies[name]
    
    def listPolicies(self):
        names = self._policies.keys()
        names.sort()
        return names
    
    def register(self, name, policy):
        """register policy"""
        assert IContainerPolicy.isImplementedBy(policy)
        self._policies[name] = policy

    def unregister(self, name):
        """unregister policy"""
        try:
            del(self._policies[name])
        except KeyError:
            pass
        
    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
        'createDefaultDocument')
    def createDefaultDocument(self, container, title):
        """Create an index according to container policy.
        """
        assert IContainer.isImplementedBy(container)
        # we use aq_parent here because without:
        # if it's a publication, self would be returned, which's metadata
        #   is not set yet
        # if it's a folder it's not the right thing anyway, so it doesn't hurt
        publication = container.aq_parent.get_publication()
        binding = container.service_metadata.getMetadata(publication)
        policy_name = binding.get('silva-publication',
            element_id='defaultdocument_policy')
        policy = self.getPolicy(policy_name)
        policy.createDefaultDocument(container, title)
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
    
class _SimpleContentPolicy(Persistent):
    
    # XXX: after Python 2.2 can be used, this should become a Singleton
    
    __implements__ = IContainerPolicy

    def createDefaultDocument(self, container, title):
        assert IContainer.isImplementedBy(container)
        container.manage_addProduct['Silva'].manage_addSimpleContent(
            'index', title)
        container.index.sec_update_last_author_info()
        
SimpleContentPolicy = _SimpleContentPolicy()
    

