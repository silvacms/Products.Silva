from Products.SilvaDocument.Document import Document, DocumentVersion
from Products.Silva.Ghost import Ghost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.Folder import manage_addFolder
from Products.Silva.Publication import manage_addPublication
from Products.Silva.silvaxml.xmlimport import BaseHandler, theElementRegistry, generateUniqueId
from Products.Silva.Link import Link, LinkVersion
from Products.ParsedXML.ParsedXML import ParsedXML
from Products.Silva import mangle

NS_URI = 'http://infrae.com/ns/silva'
# XXX Move to SilvaDocument
DOC_NS_URI = 'http://infrae.com/ns/silva_document'

def initializeElementRegistry():
    """Here the importable (namespaced!) xml elements are registered. 
    Non-Silva-Core content types probably need to register themselves in 
    their product __init__.pies
    """
    handler_map = {
        ('http://www.infrae.com/xml', 'silva_container'): SilvaHandler,
        ('http://www.infrae.com/xml', 'silva'): SilvaHandler,
        (NS_URI, 'silva'): SilvaHandler,
        (NS_URI, 'publication'): PublicationHandler,
        (NS_URI, 'folder'): FolderHandler,
        (NS_URI, 'ghost'): GhostHandler,
        (NS_URI, 'version'): VersionHandler,
        (NS_URI, 'link'): LinkHandler,
        (NS_URI, 'set'): SetHandler,
        (NS_URI, 'document'): DocumentHandler,
        }
    theElementRegistry.addHandlerMap(handler_map)

class SilvaHandler(BaseHandler):
    pass

class FolderHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'folder'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = generateUniqueId(id, self._parent)
            self._parent.manage_addProduct['Silva'].manage_addFolder(
                uid, '')
            self._result = getattr(self._parent, uid)
                
    def endElementNS(self, name, qname):
        if name == (NS_URI, 'folder'):
            self._result.set_title(
                self._metadata['silva-content']['maintitle']
                )
            self.storeMetadata()

class PublicationHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'publication'):
            id = str(attrs[(None, 'id')])
            uid = generateUniqueId(id, self._parent)
            self._parent.manage_addProduct['Silva'].manage_addPublication(
                uid, '')
            self._result = getattr(self._parent, uid)
                
    def endElementNS(self, name, qname):
        if name == (NS_URI, 'publication'):
            self._result.set_title(
                self._metadata['silva-content']['maintitle']
                )
            self.storeMetadata()
            
class VersionHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'status'): StatusHandler,
            (NS_URI, 'publication_datetime'): PublicationDateTimeHandler,
            (NS_URI, 'expiration_datetime'): ExpirationDateTimeHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'version'):
            self._id = attrs[(None, 'id')]

    def endElementNS(self, name, qname):
        self.setWorkflowVersion(self._id,self.getData('publication_datetime'), self.getData('expiration_datetime'), self.getData('status'))

class SetHandler(BaseHandler):
    def __init__(self, parent, parent_handler, options={}):
        BaseHandler.__init__(self, parent, parent_handler, options)
        self._metadata_key = None
        
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'set'):
            self._metadata_set = attrs[(None, 'id')]
            self._parent_handler._metadata[self._metadata_set] = {}
        else:
            self._metadata_key = name[1]
            
    def characters(self, chrs):
        if self._metadata_key is not None:
            self._parent_handler.setMetadata(self._metadata_set, self._metadata_key, chrs)
        
    def endElementNS(self, name, qname):
        self._metadata_key = None
        
class GhostHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): GhostContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'ghost'):
            id = str(attrs[(None, 'id')])
            uid = generateUniqueId(id, self._parent)
            ghost_object = Ghost(uid)
            self._parent.addItem(ghost_object)
            self._result = ghost_object

class GhostContentHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                id = attrs[(None, 'version_id')]
                version = GhostContent(id)
                self._parent._setObject(id, version)
                self._result = version
                updateVersionCount(self)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'ghost'):
            self.storeWorkflow()
            self.storeMetadata()
            
class LinkHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): LinkContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'link'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = generateUniqueId(id, self._parent)
            object = Link(uid)
            self._parent._setObject(uid, object)
            self._result = getattr(self._parent, uid)
        
class LinkContentHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'url'): URLHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            id = attrs[(None, 'version_id')].encode('utf-8')
            if not mangle.Id(self._parent, id).isValid():
                return
            version = LinkVersion(id, '')
            self._parent._setObject(id, version)
            self._result = getattr(self._parent, id)
            updateVersionCount(self)
            
    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self._result.set_url(self.getData('url'))
            self._result.set_title(
                self._metadata['silva-content']['maintitle'])
            self.storeWorkflow()
            self.storeMetadata()

class StatusHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('status', chrs)

class PublicationDateTimeHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('publication_datetime', chrs)

class ExpirationDateTimeHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('expiration_datetime', chrs)

class URLHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('url', chrs)

# XXX Move to SilvaDocument
class DocumentHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): DocumentContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'document'):
            id = attrs[(None, 'id')].encode('utf-8')
            uid = generateUniqueId(id, self._parent)
            object = Document(uid)
            self._parent._setObject(uid, object)
            self._result = getattr(self._parent, uid)

    def EndElementNS(self, name, qname):
        if name == (NS_URI, 'document'):
            pass
        
class DocumentContentHandler(BaseHandler):
    def getOverrides(self):
        return{
            (DOC_NS_URI, 'doc'): DocElementHandler,
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            id = attrs[(None, 'version_id')].encode('utf-8')
            if not mangle.Id(self._parent, id).isValid():
                return
            version = DocumentVersion(id, '')
            self._parent._setObject(id, version)
            self._result = getattr(self._parent, id)
            updateVersionCount(self)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self._result.set_title(
                self._metadata['silva-content']['maintitle'])
            self.storeWorkflow()
            self.storeMetadata()
        
class DocElementHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (DOC_NS_URI, 'doc'):
            self._node = self._parent.content.documentElement
            self._tree = self._parent.content
        else:
            child = self._tree.createElement(name[1])
            self._node.appendChild(child)
            self._node = child
        for ns, attr in attrs.keys():
            self._node.setAttribute(attr, attrs[(ns, attr)])
            
    def characters(self, chrs):
        textNode = self._tree.createTextNode(chrs)
        self._node.appendChild(textNode)

    def endElementNS(self, name, qname):
        if name == (DOC_NS_URI, 'doc'):
            self._node = None
        else:
            self._node = self._node.parentNode
            
def updateVersionCount(versionhandler):
    # The parent of a version is a VersionedContent object. This VC object
    # has an _version_count attribute to keep track of the number of
    # existing version objects and is the used to determine the id for a
    # new version. However, after importing, this _version_count has the
    # default value (1) and thus should be updated to reflect the highest
    # id of imported versions (+1 of course :)
    parent = versionhandler._parent
    version = versionhandler._result
    id = version.id
    try:
        id = int(id)
    except ValueError:
        # I guess this is the only reasonable thing to do - apparently 
        # this id does not have any numerical 'meaning'.
        return 
    vc = max(parent._version_count, (id + 1))
    parent._version_count = vc
    