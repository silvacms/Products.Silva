# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.14 $
"""
This module defines a class and an instance of the importer_registry,
a place to register xml_import_handlers. The handlers should be
registered at runtime (by adding some code in the __init__.py's of
products that want to support XML-importing) by calling
importer_registry.register_tag(<tag_name>, <function_reference>),
where <tag_name> is the name of the main tag of the objecttype's
xml-export (e.g.  silva_publication, silva_folder or silva_document)
and <function_reference> is a reference to the function that will
create the actual object. The function will have to support 2
arguments: object, the object in which the new object will be placed,
and node, a ParsedXML node which will be used to create the document
from.  the function should return the new object created.

??? why are the registry keys encoded by cp1252 instead of unicode strings
"""
from types import UnicodeType

DEFAULT_ENCODING = None

def encode_key(key, encoding=DEFAULT_ENCODING):
    if isinstance(key, UnicodeType) and encoding is not None:
        return key.encode(encoding)
    return key

class Error(Exception):
    pass

class ImporterRegistry:
    """A registry for importing XML.

    Do not import or use this class directly, but instead import the
    instance (importer_registry), then call the register_tag method to
    register a specific objecttype's xml import handler or
    import_function to get the handler (should probably only be called
    by xml_import_helper).  You can check whether an objecttag is
    already registered by calling the keys-method.
    """

    def __init__(self):
        self._import_handlers = {}
        self._object_initializers = {} # for post import initilization
        self._default_initializer = []
        
    def register_tag(self, tag_name, import_function):
        """
        register an import function for a tag
        """
        key = encode_key(tag_name)
        self._import_handlers[key] = import_function

    def register_initializer(self, initialization_func,
                             tag_name=None, default=None, priority=1000):
        """
        register a function as to initialize objects after
        """
        if default and not tag_name:
            self._default_initializer.insert(priority, initialization_func)
            
        elif not default and tag_name:
            initializers = self._object_initializers.setdefault(
                encode_key(tag_name), [])
            initializers.insert(priority, initialization_func)
        else:
            msg = ("can't only register initializer for tag_name "
                        "*or* as a default")
            raise Error(msg)
        
    def get_initializer(self, tag_name):
        initializers =  self._object_initializers.get( encode_key( tag_name ) )
        
        if initializers is None and self._default_initializer:
            return list(self._default_initializer)

        initializers = list(initializers) # copy the list to modify
        initializers.extend(self._default_initializer)
        return initializers

    def import_function(self, tag_name):
        """Returns the import_function handler for tag_name
           or None if none found """
        return self._import_handlers.get( encode_key(tag_name) )

    def keys(self):
        """Returns a list of registered objecttags"""
        return self._import_handlers.keys()


importer_registry = ImporterRegistry()
register_importer = importer_registry.register_tag
register_initializer = importer_registry.register_initializer
get_initializer = importer_registry.get_initializer
get_importer = importer_registry.import_function

# Some helper functions
def xml_import_helper(object, node):
    """Parses node into object."""
    
    import_handler = get_importer( node.nodeName )
    init_handlers  = get_initializer( node.nodeName )
    
    if import_handler is None:
        return

    new_object = import_handler(object, node)

    if new_object is not None:
        for ih in init_handlers:
            ih(object, new_object, node)

    return None

def get_xml_id(node):
    id = None
    for attr in node._attributes:
        if attr[1] == u'id':
            # the id MUST be ASCII
            id = attr[4].encode('ascii')
    if not id:
        raise Error, 'No id found'
    return id

def get_xml_title(node):
    title = 'unknown'
    for child in node.childNodes:
        if child.nodeName == u'title' and len(child.childNodes) > 0:
            title = child.childNodes[0].nodeValue
    return title

