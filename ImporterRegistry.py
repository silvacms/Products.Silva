"""This module defines a class and an instance of the importer_registry, a place
    to register xml_import_handlers. The handlers should be registered at runtime
    (by adding some code in the __init__.py's of products that want to support
    XML-importing) by calling importer_registry.register_tag(<tag_name>, <function_reference>),
    where <tag_name> is the name of the main tag of the objecttype's xml-ecport (e.g.
    silva_publication, silva_folder or silva_document) and <function_reference> is a
    reference to the function that will create the actual object. The function will
    have to support 2 arguments: object, the object in which the new object will be
    placed, and node, a ParsedXML node which will be used to create the document from.
    """

class ImporterRegistry:
    """This class will contain the registry for importing XML. Do not import or use this
    class directly, but instead import the instance (importer_registry), then call the
    register_tag method to register a specific objecttype's xml import handler or
    import_function to get the handler (should probably only be called by xml_import_helper).
    You can check whether an objecttag is already registered by calling the keys-method"""

    _reg = {}

    def register_tag(self, tag_name, import_function):
        """Register a tag"""
        self._reg[tag_name.encode('cp1252')] = import_function

    def import_function(self, tag_name):
        """Returns the import_function handler for tag_name"""
        return self._reg.get(tag_name.encode('cp1252'), None)

    def keys(self):
        """Returns a list of registered objecttags"""
        return self._reg.keys()

    def __setitem__(self, key, value):
        raise Exception, 'Read only object!'

    __setattr__ = __setitem__

importer_registry = ImporterRegistry()

# Some helper functions
def xml_import_helper(object, node):
    """Parses node into object."""
    func = importer_registry.import_function(node.nodeName.encode('cp1252'))
    if func:
        func(object, node)

def get_xml_id(node):
    id = None
    for attr in node._attributes:
        if attr[1] == u'id':
            print attr
            id = attr[4].encode('cp1252')
    if not id:
        raise Exception, 'No id found'
    return id

def get_xml_title(node):
    title = ''
    for child in node.childNodes:
        if child.nodeName == u'title':
            title = child.childNodes[0].nodeValue.encode('cp1252')
    return title

