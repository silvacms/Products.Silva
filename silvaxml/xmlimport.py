import sys, string
from xml.sax.handler import ContentHandler
from DateTime import DateTime

class XMLImportError(Exception):
    pass

class XMLOverridableElementRegistry:
    """An element registry which can be overridden while handling events.
    """
    def __init__(self):
        self._mapping = {}
        self._stack = []

    def addHandlerMap(self, handler_map):
        for element, handler in handler_map.items():
            self._mapping[element] = [handler]
            
    def _pushOverride(self, element, handler):
        self._mapping.setdefault(element, []).append(handler)
    
    def pushOverrides(self, overrides):
        for element, handler in overrides.items():
            self._pushOverride(element, handler)
        self._stack.append(overrides.keys())
      
    def _popOverride(self, element):
        stack = self._mapping[element]
        stack.pop()
        if not stack:
            del self._mapping[element]
    
    def popOverrides(self):
        elements = self._stack.pop()
        for element in elements:
            self._popOverride(element)
            
    def getXMLElementHandler(self, element):
        try:
            return self._mapping[element][-1]
        except KeyError:
            return None

theElementRegistry = XMLOverridableElementRegistry()

getXMLElementHandler = theElementRegistry.getXMLElementHandler

class SaxImportHandler(ContentHandler):
    def __init__(self, start_object, settings=None):
        self._registry = theElementRegistry
        self._handler_stack = []
        self._depth_stack = []
        self._object = start_object
        self._settings = settings
        # XXX Might need this later for context sensitive parsing
        self._depth = 0
        
    def startDocument(self):
        # XXX probably some export metadata should be read and handled here.
        # Export will have some configuration options that may impact the
        # import process.
        # XXX maybe handle encoding?
        pass 
    
    def endDocument(self):
        # XXX finalization
        pass
    
    def startElementNS(self, name, qname, attrs):
        factory = self._registry.getXMLElementHandler(name)
        if factory is None:
            handler = self._handler_stack[-1]
        else:
            if self._handler_stack:
                parent_handler = self._handler_stack[-1]
                object = parent_handler.getResult()
            else:
                parent_handler = None
                object = self._object
            handler = factory(object, parent_handler, self._settings)
            self._registry.pushOverrides(handler.getOverrides())
            self._handler_stack.append(handler)
            self._depth_stack.append(self._depth)
        handler.startElementNS(name, qname, attrs)
        self._depth += 1

    def endElementNS(self, name, qname):
        self._depth -= 1
        handler = self._handler_stack[-1]
        if self._depth == self._depth_stack[-1]:
            self._handler_stack.pop()
            self._depth_stack.pop()
            self._registry.popOverrides()
        handler.endElementNS(name, qname)
        
    def characters(self, chrs):
        handler = self._handler_stack[-1]
        handler.characters(chrs)
    
class BaseHandler:
    def __init__(self, parent, parent_handler, settings=None):
        # it is essential NOT to confuse self._parent and
        # self._parent_handler. The is the parent object as it is being
        # constructed from the import, the latter is the handler that is 
        # handling the parent of the current handled element.
        self._parent = parent
        self._parent_handler = parent_handler
        self._result = None
        self._data = {}
        self._metadata_set = None
        self._metadata_key = None
        self._metadata = {}
        self._settings = settings
        self._workflow = {}
        
    def getOverrides(self):
        """Returns a dictionary of overridden handlers for xml elements. 
        (The handlers override any registered handler for that element, but
        getOverrides() can be used to 'override' tags that aren't
        registered.)
        """
        return {}

    def setData(self, key, value):
        """Many sub-elements with text-data use this to pass that data to
        their parent (self._parent_handler.setData(foo, bar))
        """
        self._data[key] = value

    def getData(self, key):
        if self._data.has_key(key):
            return self._data[key]
        return None

    def setMetadata(self, set, key, value):
        # XXX Hardcoded. Will update this to look up the types in a
        # dictionary. 
        if set == 'silva-extra' and value:
            if key == 'modificationtime' or key == 'creationtime' or \
            key == 'publicationtime' or key == 'expirationtime':
                value = DateTime(value)
        self._metadata[set][key] = value

    def setWorkflowVersion(
        self, version_id, publicationtime, expirationtime, status):
        if publicationtime:
            publicationtime = DateTime(publicationtime)
        if expirationtime:
            expirationtime = DateTime(expirationtime)
            
        self._parent_handler._workflow[version_id] = (
            publicationtime, expirationtime, status)
        
    def getMetadata(self, set, key):
        return self._metadata[set][key]

    def getWorkflowVersion(self, version_id):
        return self._parent_handler._workflow[version_id]
    
    def getResult(self):
        if self._result is not None:
            return self._result
        else:
            return self._parent
    
    def startElementNS(self, name, qname, attrs):
        pass
    
    def endElementNS(self, name, qname):
        pass

    def characters(self, chrs):
        pass

    def storeMetadata(self):
        content = self._result
        metadata_tool = content.service_metadata
        metadata = {}
        binding = metadata_tool.getMetadata(content)
        for set_name in binding.collection.keys():
            set = binding.collection[set_name]
            element_names = self._metadata[set.id].keys()
            # Set data
            errors = binding._setData(
                namespace_key=set.metadata_uri,
                data=self._metadata[set.id],
                reindex=1
                )

            if errors:
                raise ValidationError(
                    "%s %s" % (str(content.getPhysicalPath()),str(errors)))

    def storeWorkflow(self):
        content = self._result
        version_id = content.id
        publicationtime, expirationtime, status = self.getWorkflowVersion(version_id)
        if status == 'unapproved':
            self._parent._unapproved_version = (
                version_id,
                publicationtime,
                expirationtime
                )
        elif status == 'approved':
            self._parent._approved_version = (
                version_id,
                publicationtime,
                expirationtime
                )
        elif status == 'public':
            self._parent._public_version = (
                version_id,
                publicationtime,
                expirationtime
                )
        else:
            previous_versions = self._parent._previous_versions or []
            previous_version = (
                version_id,
                publicationtime,
                expirationtime
                )
            previous_versions.append(previous_version)
            self._parent._previous_versions = previous_versions
        
def generateUniqueId(org_id, context):
        i = 0
        id = org_id
        ids = context.objectIds()
        while id in ids:
            i += 1
            add = ''
            if i > 1:
                add = str(i)
            id = 'copy%s_of_%s' % (add, org_id)
        return id
   