def import_xml_helper(object, node):
    """Parses node into object."""
    for child in node.childNodes:
        func = importer_registry[node.nodeName]
        if func:
            func(object, child)

class ImporterRegistry:
    """This class will contain the registry for importing XML"""
    def __init__(self):
        self._reg = {}

    def register_tag(self, tag_name, import_function):
        """Register a tag"""
        self._reg[tag_name] = import_function

    def import_function(self, tag_name):
        """Returns the import_function handler for tag_name"""
        return self._reg.get(tag_name, None)

importer_registry = ImporterRegistry()