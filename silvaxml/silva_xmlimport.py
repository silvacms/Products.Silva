from xmlimport import SaxImportHandler, BaseHandler
import xml.sax
from xml.sax.handler import feature_namespaces

NS_URI = 'http://infrae.com/ns/silva/0.5'

class SilvaHandler(BaseHandler):
    pass

class FolderHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'folder'):
            folder_object = Folder(attrs[(None, 'id')])
            self._parent.addItem(folder_object)
            self._result = folder_object

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'folder'):
            self._result.setTitle(self._metadata['silva_metadata']['maintitle'])
                
class VersionHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'status'): StatusHandler,
            (NS_URI, 'publication_date'): PublicationDateHandler,
            (NS_URI, 'expiration_date'): ExpirationDateHandler
            }

    def startElementNS(self, name, qname, attrs):
        self._id = attrs[(None, 'id')]

    def endElementNS(self, name, qname):
        self._parent.setWorkflow(
            self._id,
            self.getData('status'),
            self.getData('publication_date'),
            self.getData('expiration_date'))

class SetHandler(BaseHandler):
    def __init__(self, parent, parent_handler):
        BaseHandler.__init__(self, parent, parent_handler)
        self._metadata_key = None
        
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'set'):
            self._metadata_set = attrs[(None, 'id')]
            self._parent_handler._metadata[self._metadata_set] = {}
        else:
            # XXX do something other than ignore the namespace
            namespace, self._metadata_key = name
            
    def characters(self, chrs):
        if self._metadata_key is not None:
            self._parent_handler._metadata[self._metadata_set][self._metadata_key] = chrs
        
    def endElementNS(self, name, qname):
        self._parent.addMetadataSet(self._metadata_set, self._parent_handler._metadata[self._metadata_set])
        self._metadata_key = None
        
class GhostHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): GhostContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'ghost'):
            ghost_object = Ghost(attrs[(None, 'id')])
            self._parent.addItem(ghost_object)
            self._result = ghost_object

class GhostContentHandler(BaseHandler):
    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                id = attrs[(None, 'version_id')]
                version = GhostContent(id)
                self._parent.addVersion(version)
                self._result = version

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'ghost'):
            if self._data.has_key('title'):
                self._result.setTitle(self.getData('title'))
            for key in self._metadata.keys():
                self._result.addMetadata(key, self.getMetadata(key))

class LinkHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'content'): LinkContentHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'link'):
            link_object = Link(attrs[(None, 'id')])
            self._parent.addItem(link_object)
            self._result = link_object
            
class LinkContentHandler(BaseHandler):
    def getOverrides(self):
        return {
            (NS_URI, 'url'): URLHandler
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                id = attrs[(None, 'version_id')]
                version = LinkContent(id)
                self._parent.addVersion(version)
                self._result = version

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            self._result.setUrl(self.getData('url'))
            self._result.setTitle(self._metadata['silva_metadata']['maintitle'])

class StatusHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('status', chrs)

class PublicationDateHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('publication_date', chrs)

class ExpirationDateHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('expiration_date', chrs)

class TitleHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('title', chrs)

class URLHandler(BaseHandler):
    def characters(self, chrs):
        self._parent_handler.setData('url', chrs)

# From here on down, fake Silva objects are defined. XXX These need their
# interfaces changed so that they match real Silva objects for the relevant
# methods. If that works, they can be killed. MWOOHAHAHA!
       
class Folder:
    def __init__(self, id):
        self.id = id
        self._contents = []
        self._title = None
        self._metadata = {}
        
    def addItem(self, item):
        self._contents.append(item)
        item.parent = self

    def getItems(self):
        return self._contents

    def addMetadataSet(self, set_name, set):
        self._metadata[set_name] = set

    def getMetadata(self):
        return self._metadata

    def setTitle(self, title):
        self._title = title
        
    def getTitle(self):
        return self._title
    
class VersionedContent:
    def __init__(self, id):
        self.id = id
        self._workflow = {}
        self._versions = {}

    def getVersion(self, version_id):
        return self._versions[version_id]

    def addVersion(self, version):
        self._versions[version.id] = version

    def setWorkflow(self, id, status, publication_datetime, expiration_datetime):
        self._workflow[id] = status, publication_datetime, expiration_datetime

    def getWorkflow(self):
        return self._workflow
    
class Link(VersionedContent):
    pass

class Ghost(VersionedContent):
    pass

class Version:
    def __init__(self, id):
        self.id = id
        self._status = None
        self._publicationDate = None
        self._expirationDate = None

class Workflow:
    def __init__(self):
        pass
    
class Content:
    def __init__(self, id):
        self.id = id
        self._metadata = {}
        self._title = None
        
    def addMetadataSet(self, set_name, set):
        self._metadata[set_name] = set

    def getMetadata(self):
        return self._metadata

    def setTitle(self, title):
        self._title = title
        
    def getTitle(self):
        return self._title
    
class LinkContent(Content):
    def setUrl(self, url):
        self._url = url
        
    def getUrl(self):
        return self._url

# XXX This will be replaced by just the registration. A global variable
# like handler_map? Or will that happen somewhere else?

def test(source_filename):
    # XXX Metadata is not handled generically!
    handler_map = {
        (NS_URI, 'silva'): SilvaHandler,
        (NS_URI, 'folder'): FolderHandler,
        (NS_URI, 'ghost'): GhostHandler,
        (NS_URI, 'title'): TitleHandler,
        (NS_URI, 'version'): VersionHandler,
        (NS_URI, 'link'): LinkHandler,
        (NS_URI, 'set'): SetHandler,
        }
    source_file = open(source_filename, 'r')
    root = Folder('root')
    handler = SaxImportHandler(root, handler_map)
    parser = xml.sax.make_parser()
    parser.setFeature(feature_namespaces, 1)
    parser.setContentHandler(handler)
    parser.parse(source_file)
    source_file.close()
    return root

if __name__ == '__main__':
    test('test.xml')