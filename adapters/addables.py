from zope.interface import implements

import Globals
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.Silva import SilvaPermissions, interfaces
from Products.Silva.adapters import adapter
from Products.Silva.adapters.interfaces import IAddables

class BaseAddablesAdapter(adapter.Adapter):

    implements(IAddables)
    security = ClassSecurityInfo()
    
    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'getAddables')
    def getAddables(self):
        """return a list of Metatypes that are addable to this container."""
        addables = self._getCurrentAddables()
        if addables is not None:
            return addables
        return getAddablesAdapter(self.context.aq_parent).getAddables()
    
class AddablesAdapter(BaseAddablesAdapter):

    security = ClassSecurityInfo()
    
    def __init__(self, context):
        BaseAddablesAdapter.__init__(self, context)
        if not hasattr(self.context, '__addables__'):
            self.context.__addables__ = []

    def _getCurrentAddables(self):
        return self.context.__addables__
    
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'setAddables')
    def setAddables(self, addables):
        """set the the Metatypes that are addable to this container."""
        self.context.__addables__ = addables
        
class PublicationAddablesAdapter(BaseAddablesAdapter):

    security = ClassSecurityInfo()

    def _getCurrentAddables(self):
        return self.context._addables_allowed_in_publication
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'setAddables')
    def setAddables(self, addables):
        """set the the Metatypes that are addable to this container."""
        self.context.set_silva_addables_allowed_in_publication(addables)
        
class RootAddablesAdapter(BaseAddablesAdapter):

    security = ClassSecurityInfo()

    def _getCurrentAddables(self):
        return self.context._addables_allowed_in_publication
    
    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'getAddables')
    def getAddables(self):
        """return a list of Metatypes that are addable to this container."""
        addables = self._getCurrentAddables()
        if addables is not None:
            return addables
        return self.get_silva_addables_all()
        
    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'setAddables')
    def setAddables(self, addables):
        """set the the Metatypes that are addable to this container."""
        self.context.set_silva_addables_allowed_in_publication(addables)
        
Globals.InitializeClass(AddablesAdapter)

module_security = ModuleSecurityInfo('Products.Silva.adapters.addables')

module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                  'getAddablesAdapter')
def getAddablesAdapter(context):
    if interfaces.IRoot.providedBy(context):
        return RootAddablesAdapter(context).__of__(context)
    elif interfaces.IPublication.providedBy(context):
        return PublicationAddablesAdapter(context).__of__(context)
    else:
        return AddablesAdapter(context).__of__(context)
