# Copyright (c) 2002-2005 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: assetregistry.py,v 1.3 2005/01/19 14:26:09 faassen Exp $
from Products.Silva import ExtensionRegistry

"""mimetype-to-asset-factory registry"""

_mimetype_to_factory = {}

def getFactoryForMimetype(context, mimetype):
    # Return None if no factory registered
    factory, extension = _mimetype_to_factory.get(mimetype, (None, None))
    if context.service_extensions.is_installed(extension):
        # Check to see if the extension is actually installed
        return factory
    else:
        return None

def registerFactoryForMimetype(mimetype, factory, silvaextension):
    # This will overwrite earlier registration for the same mimetype
    _mimetype_to_factory[mimetype] = (factory, silvaextension)
    
def registerFactoryForMimetypes(mimetypes, factory, silvaextension):
    # Utility for lists of mimetypes
    for mimetype in mimetypes:
        registerFactoryForMimetype(mimetype, factory, silvaextension)
        
def unregisterFactory(factory):
    types = []
    for type, spec in _mimetype_to_factory.items():
        currentfactory, extensionname = spec
        if factory is currentfactory:
            types.append(type)
    for type in types:
        unregisterMimetype(type)
            
def unregisterMimetype(mimetype):
    if _mimetype_to_factory.has_key(mimetype):
        del _mimetype_to_factory[mimetype]
