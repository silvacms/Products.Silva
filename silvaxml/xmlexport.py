"""
An alternative XML export for Silva content. This will eventually replace
the existing export machinery.
"""
from StringIO import StringIO
from xml.sax import saxutils
from Products.Silva.File import File
from Products.Silva.Folder import Folder
from Products.Silva.Ghost import Ghost, GhostVersion
from Products.Silva.GhostFolder import GhostFolder
from Products.Silva.Link import Link, LinkVersion
from Products.Silva.interfaces import IPublication
from Products.SilvaMetadata.Compatibility import getToolByName
from Products.SilvaDocument.Document import Document, DocumentVersion
from Products.ParsedXML.DOM.Core import Node
from DateTime import DateTime

class XMLSourceRegistry:
    """Registers Content Types to XML Sources that generate Sax-events.
    """
    def __init__(self):
        self._mapping = {}
        self._fallback = None
        
    def registerFallbackXMLSource(self, fallback):
        self._fallback = fallback
        
    def registerXMLSource(self, klass, xml_source):
        self._mapping[klass] = xml_source
        
    def getXMLSource(self, context):
        xmlsource = self._mapping.get(context.__class__, None)
        if xmlsource is None:
            if self._fallback is not None:
                return self._fallback(context)
            else:
                return None
        return xmlsource(context)

theXMLSourceRegistry = XMLSourceRegistry()

getXMLSource = theXMLSourceRegistry.getXMLSource

SilvaDocumentNS = "http://infrae.com/ns/silva_document"

def initializeXMLSourceRegistry():
    """Here the actual content types are registered. Non-Silva-Core content
    types probably need to register themselves in in their product
    __init__.pies
    """
    reg = theXMLSourceRegistry
    reg.registerXMLSource(File, FileXMLSource)
    reg.registerXMLSource(Folder, FolderXMLSource)
    reg.registerXMLSource(Link, LinkXMLSource)
    reg.registerXMLSource(LinkVersion, LinkVersionXMLSource)
    reg.registerXMLSource(Ghost, GhostXMLSource)
    reg.registerXMLSource(GhostVersion, GhostVersionXMLSource)
    reg.registerXMLSource(GhostFolder, GhostFolderXMLSource)
    # XXX move to SilvaDocument
    reg.registerXMLSource(Document, DocumentXMLSource)
    reg.registerXMLSource(DocumentVersion, DocumentVersionXMLSource)
    
class BaseXMLSource:
    def __init__(self, context):
        self.context = context

    def xmlToString(self, settings):
        """Output the XML as a string
        """
        f = StringIO()
        self.xmlToFile(f, settings)
        result = f.getvalue()
        f.close()
        return result
    
    def xmlToFile(self, file, settings):
        """Output the XML to a file
        """
        reader = saxutils.XMLGenerator(file, 'UTF-8')
        self.xmlToSax(reader, settings)
        
    def xmlToSax(self, reader, settings):
        """Export self.context to XML Sax-events 
        """
        reader.startPrefixMapping(None, self.ns_default)
        reader.startPrefixMapping('doc', SilvaDocumentNS)
        for set in self.context.service_metadata.collection.getMetadataSets(
            ):
            reader.startPrefixMapping(set.id, set.metadata_uri)
        # XXX start all registered prefixmappings here
        self._startElement(
            reader,
            'silva',
            {'url':self.context.absolute_url(),
            'path':'/'.join(self.context.getPhysicalPath()),
            'datetime':DateTime().HTML4()})
        self._sax(reader, settings)
        self._endElement(reader, 'silva')

    def _sax(self, reader, settings):
        """To be overridden in subclasses
        """
        raise NotImplemented

    def _metadata(self, reader, settings):
        """Export the metadata to XML Sax-events
        """
        metadata_service = getToolByName(self.context, 'portal_metadata')
        binding = metadata_service.getMetadata(self.context)
        self._startElement(reader, 'metadata', {})
        for set_id in binding.collection.keys():
            prefix, namespace = binding.collection[set_id].getNamespace()
            self._startElement(reader, 'set', {'id': set_id})
            for key, value in binding._getData(set_id).items():
                self._startElementNS(reader, namespace, key, {})
                if key == 'comment' or key == 'description':
                    print repr(key), repr(value)
                if value:
                    if type(value) == type(DateTime()):
                        value = value.HTML4()
                    elif type(value) == type(''):
                        value = unicode(value, 'utf-8')
                    reader.characters(value)
                self._endElementNS(reader, namespace, key)
            self._endElement(reader, 'set')
        self._endElement(reader, 'metadata')

    def _startElementNS(self, reader, ns, name, attrs=None):
        """Starts a named XML element in the provided namespace with
        optional attributes
        """
        d = {}
        
        if attrs is not None:
            for key, value in attrs.items():
                d[(None, key)] = value
        reader.startElementNS(
            (ns, name),
            None,
            d)
        
    def _endElementNS(self, reader, ns, name):
        """Ends a named element in the provided namespace
        """
        reader.endElementNS(
            (ns, name),
            None)
        
    def _startElement(self, reader, name, attrs=None):
        """Starts a named XML element in the default namespace with optional
        attributes
        """
        self._startElementNS(reader, self.ns_default, name, attrs)
        
    def _endElement(self, reader, name):
        """Ends a named element in the default namespace
        """
        self._endElementNS(reader, self.ns_default, name)
            
class SilvaBaseXMLSource(BaseXMLSource):
    """Base class to declare the Silva namespace.
    """
    ns_default = 'http://infrae.com/ns/silva/0.5'

class VersionXMLSource(SilvaBaseXMLSource):
    """Base class for Versions. May have its own methods in the future.
    """
    
class VersionedContentXMLSource(SilvaBaseXMLSource):
    """Base Class for all versioned content
    """
    def _workflow(self, reader, settings):
        """Export the XML for the versioning workflow
        """
        if not settings.workflow():
            return
        self._startElement(reader, 'workflow', {})
        version = self.context.get_unapproved_version_data()
        if version[0]:
            self._workflow_version(version, 'unapproved', reader, settings)
        version = self.context.get_approved_version_data()
        if version[0]:
            self._workflow_version(version, 'approved', reader, settings)
        version = self.context.get_public_version_data()
        if version[0]:
            self._workflow_version(version, 'public', reader, settings)
        for version in self.context.get_previous_versions_data():
            self._workflow_version(version, 'closed', reader, settings)
        self._endElement(reader, 'workflow')

    def _workflow_version(self, version, status, reader, settings):
        """Export the XML for the different workflow versions. (Right now:
        Published, Approved, Unapproved, and Closed, but to the XML these
        are arbitrary)
        """
        id, publication_datetime, expiration_datetime = version
        self._startElement(reader, 'version', {'id':id})
        self._startElement(reader, 'status', {})
        reader.characters(status)
        self._endElement(reader, 'status')
        self._startElement(reader, 'publication_datetime', {})
        if publication_datetime:
            if type(publication_datetime) == type(DateTime()):
                reader.characters(str(publication_datetime.HTML4()))
            else:
                reader.characters(unicode(str(publication_datetime)))
        self._endElement(reader, 'publication_datetime')
        self._startElement(reader, 'expiration_datetime', {})
        if expiration_datetime:
            if type(expiration_datetime) == type(DateTime()):
                reader.characters(str(expiration_datetime.HTML4()))
            else:
                reader.characters(unicode(str(expiration_datetime)))
        self._endElement(reader, 'expiration_datetime')
        self._endElement(reader, 'version')
        
    def _versions(self, reader, settings):
        """Export the XML of the versions themselves.
        """
        if settings.allVersions():
            for version in self.context.objectValues():
                getXMLSource(version)._sax(reader, settings)
        else:
            # XXX handle single version export. Is previewable right? Is
            # there a better method that is guaranteed to return a best
            # guess version?
            getXMLSource(
                self.context.get_previewable())._sax(reader, settings)
            
    def _metadata(self, reader, settings):
        """Versioned Content has no metadata, the metadata is all on the
        versions themselves.
        """
        return 
    
class FileXMLSource(SilvaBaseXMLSource):
    """Export a Silva File object to XML. 
    """
    # XXX This needs to change or be removed. It's completely useless as is.
    def _sax(self, reader, settings):
        self._startElement(
            reader,
            'file',
            {'id':self.context.id, 'url':self.context.get_download_url()})
        reader.characters(self.context.title)
        self._endElement(reader, 'file')

class FolderXMLSource(SilvaBaseXMLSource):
    """Export a Silva Folder object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(reader, 'folder', {'id':self.context.id})
        self._metadata(reader, settings)
        self._startElement(reader, 'content', {})
        for object in self.context.get_ordered_publishables():
            if (IPublication.isImplementedBy(object) and 
                    not self.context.with_sub_publications):
                continue
            getXMLSource(object)._sax(reader, settings)
        self._endElement(reader, 'content')
        self._endElement(reader, 'folder')

class LinkXMLSource(VersionedContentXMLSource):
    """Export a Silva Link object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(reader, 'link', {'id': self.context.id})
        self._workflow(reader, settings)
        self._versions(reader, settings)
        self._endElement(reader, 'link')

class LinkVersionXMLSource(VersionXMLSource):
    """Export a version of a Silva Link object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(
            reader, 'content', {'version_id': self.context.id})
        self._metadata(reader, settings)
        self._startElement(reader, 'url', {})
        reader.characters(self.context.get_url())
        self._endElement(reader, 'url')
        self._endElement(reader, 'content')

class GhostXMLSource(VersionedContentXMLSource):
    """Export a Silva Ghost object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(reader, 'ghost', {'id': self.context.id})
        self._workflow(reader, settings)
        self._versions(reader, settings)
        self._endElement(reader, 'ghost')

class GhostVersionXMLSource(VersionXMLSource):
    """Export a verson of a Silva Ghost object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(
            reader, 'content', {'version_id': self.context.id})
        content = self.context.get_haunted_unrestricted().get_viewable()
        contenttype = self.context.get_haunted_unrestricted().meta_type
        self._startElement(reader, 'metatype', {})
        reader.characters(contenttype)
        self._endElement(reader, 'metatype')
        if content is None:
            self._startElement(reader, 'broken', {})
            self._endElement(reader, 'broken')
        else:
            self._startElement(reader, 'haunted_url', {})
            reader.characters(self.context.get_haunted_url())
            self._endElement(reader, 'haunted_url')
            getXMLSource(content)._sax(reader, settings)
        self._endElement(reader, 'content')
        
class GhostFolderXMLSource(SilvaBaseXMLSource):
    """Export a Silva Ghost Folder object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(reader, 'ghost_folder', {'id': self.context.id})
        self._metadata(reader, settings)
        self._startElement(reader, 'content', {})
        content = self.context.get_haunted_unrestricted()
        contenttype = self.context.get_haunted_unrestricted().meta_type
        self._startElement(reader, 'metatype', {})
        reader.characters(contenttype)
        self._endElement(reader, 'metatype')
        self._startElement(reader, 'haunted_url', {})
        reader.characters(self.context.get_haunted_url())
        self._endElement(reader, 'haunted_url')
        if content is None:
            return
        self._startElement(reader, 'content', {})
        for object in content.get_ordered_publishables():
            if (IPublication.isImplementedBy(object) and 
                    not self.context.with_sub_publications):
                continue
            getXMLSource(object)._sax(reader, settings)
        self._endElement(reader, 'content')      
        self._endElement(reader, 'content')      
        self._endElement(reader, 'ghost_folder')      

# XXX Move to SilvaDocument

class DocumentXMLSource(VersionedContentXMLSource):
    """Export a Silva Document object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(reader, 'document', {'id': self.context.id})
        self._workflow(reader, settings)
        self._versions(reader, settings)
        self._endElement(reader, 'document')

class DocumentVersionXMLSource(VersionXMLSource):
    """Export a version of a Silva Document object to XML.
    """
    def _sax(self, reader, settings):
        self._startElement(
            reader, 'content', {'version_id': self.context.id})
        self._metadata(reader, settings)
        node = self.context.content.documentElement
        self._sax_node(node, reader, settings)
        self._endElement(reader, 'content')

    def _sax_node(self, node, reader, settings):
        """Export child nodes of a (version of a) Silva Document to XML
        """
        attributes = {}
        if node.attributes:
            for key in node.attributes.keys():
                attributes[key] = node.attributes[key].value
        self._startElementNS(reader, SilvaDocumentNS, node.nodeName, attributes)
        text = ''
        if node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType == Node.TEXT_NODE:
                    if child.nodeValue:
                        reader.characters(child.nodeValue)
                elif child.nodeType == Node.ELEMENT_NODE:
                    self._sax_node(child, reader, settings)
        else:
            if node.nodeValue:
                reader.characters(node.nodeValue)
        self._endElementNS(reader, SilvaDocumentNS, node.nodeName)
        
class ExportSettings:
    def __init__(self):
        self._workflow = 1
        self._all_versions = 1

    def setOnlyPublishedNoWorkflow(self):
        self._workflow = 0
        self._all_versions = 0

    def workflow(self):
        return self._workflow

    def allVersions(self):
        return self._all_versions