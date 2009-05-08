# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ModuleSecurityInfo
from Products.Silva import SilvaPermissions
from silva.core.interfaces import ISilvaObject

from zope.component.interfaces import IFactory
from zope.component import queryUtility

### XXX: I am not sure I should make a file for that, but a need to
### access some restricted code, so it have to be like that.
module_security = ModuleSecurityInfo('Products.Silva.adapters.views')

module_security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                                  'getView')
def getAddView(context, meta_type):
    """This search if there is factory to create the content,
    otherwise return the default add_form from Silva views.
    """
    factory = queryUtility(IFactory, name=meta_type)
    if factory:
        request = context.REQUEST
        # Search the silva context. Now we might get a context which
        # represent a folder in the silva views machinery.
        while not ISilvaObject.providedBy(context):
            context = context.aq_parent
        return factory(context, request).__of__(context)
    return context.service_view_registry.get_view('add', meta_type).add_form



