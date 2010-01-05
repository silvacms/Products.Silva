# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

import Globals
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from Products.Silva import SilvaPermissions
from silva.core import interfaces

class BaseAddablesAdapter(grok.Adapter):

    grok.implements(interfaces.IAddables)
    grok.baseclass()

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

    grok.context(interfaces.ISilvaObject)

    security = ClassSecurityInfo()

    def __init__(self, context):
        super(AddablesAdapter, self).__init__(context)
        if not hasattr(self.context, '__addables__'):
            self.context.__addables__ = []

    def _getCurrentAddables(self):
        return self.context.__addables__

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'setAddables')
    def setAddables(self, addables):
        """set the the Metatypes that are addable to this container."""
        self.context.__addables__ = addables
Globals.InitializeClass(AddablesAdapter)

class ContainerAddablesAdapter(BaseAddablesAdapter):

    grok.context(interfaces.IContainer)

    security = ClassSecurityInfo()

    def _getCurrentAddables(self):
        return self.context._addables_allowed_in_container

    security.declareProtected(SilvaPermissions.ApproveSilvaContent,
                              'setAddables')
    def setAddables(self, addables):
        """set the the Metatypes that are addable to this container."""
        self.context.set_silva_addables_allowed_in_container(addables)
Globals.InitializeClass(ContainerAddablesAdapter)

class RootAddablesAdapter(ContainerAddablesAdapter):

    grok.context(interfaces.IRoot)

    security = ClassSecurityInfo()
    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'getAddables')
    def getAddables(self):
        """return a list of Metatypes that are addable to this container."""
        addables = self._getCurrentAddables()
        if addables is not None:
            return addables
        return self.get_silva_addables_all()
Globals.InitializeClass(RootAddablesAdapter)


module_security = ModuleSecurityInfo('Products.Silva.adapters.addables')
module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                 'getAddablesAdapter')
def getAddablesAdapter(context):
    return interfaces.IAddables(context)
