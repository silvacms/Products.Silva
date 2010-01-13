""" 
The new and improved XML export for Silva content. This will replace
the existing export machinery.
"""
from StringIO import StringIO
from sprout.saxext import xmlexport
from Products.ParsedXML.DOM.Core import Node
from DateTime import DateTime
from Products.Silva.interfaces import IPublication
from Products.Silva.adapters import version_management

NS_SILVA = 'http://infrae.com/ns/silva'
NS_SILVA_CONTENT = 'http://infrae.com/namespaces/metadata/silva'
NS_SILVA_EXTRA = 'http://infrae.com/namespaces/metadata/silva-extra'

theXMLExporter = xmlexport.Exporter(NS_SILVA)

def initializeXMLExportRegistry():
    """Here the actual content types are registered. Non-Silva-Core content
    types need to register themselves in in their product
    __init__.pies
    """
    from Products.Silva.File import ZODBFile, FileSystemFile
    from Products.Silva.Root import Root
    from Products.Silva.Folder import Folder
    from Products.Silva.Publication import Publication
    from Products.Silva.Ghost import Ghost, GhostVersion
    from Products.Silva.GhostFolder import GhostFolder
    from Products.Silva.Link import Link, LinkVersion
    from Products.Silva.Image import Image
    from Products.Silva.AutoTOC import AutoTOC
    from Products.Silva.Indexer import Indexer
    exporter = theXMLExporter
    exporter.registerNamespace(
        'silva-content',
        NS_SILVA_CONTENT)
    exporter.registerNamespace(
        'silva-extra',
        NS_SILVA_EXTRA)
    exporter.registerProducer(SilvaExportRoot, SilvaExportRootProducer)
    exporter.registerProducer(Folder, FolderProducer)
    exporter.registerProducer(Link, LinkProducer)
    exporter.registerProducer(LinkVersion, LinkVersionProducer)
    exporter.registerProducer(Ghost, GhostProducer)
    exporter.registerProducer(GhostVersion, GhostVersionProducer)
    exporter.registerProducer(GhostFolder, GhostFolderProducer)
    exporter.registerProducer(Root, PublicationProducer)
    exporter.registerProducer(Publication, PublicationProducer)
    exporter.registerProducer(ZODBFile, FileProducer)
    exporter.registerProducer(FileSystemFile, FileProducer)
    exporter.registerProducer(Image, ImageProducer)
    exporter.registerProducer(AutoTOC, AutoTOCProducer)
    exporter.registerProducer(Indexer, IndexerProducer)
    exporter.registerFallbackProducer(ZexpProducer)

class SilvaBaseProducer(xmlexport.BaseProducer):
    def metadata(self):
        """Export the metadata
        """
        metadata_service = self.context.service_metadata
        binding = metadata_service.getMetadata(self.context)
        self.startElement('metadata')
        set_ids = binding.collection.keys()
        set_ids.sort()
        for set_id in set_ids:
            set_obj = binding.collection[set_id]
            prefix, namespace = set_obj.getNamespace()
            if (namespace != NS_SILVA_CONTENT and
                namespace != NS_SILVA_EXTRA):
                self.handler.startPrefixMapping(prefix, namespace)
            self.startElement('set', {'id': set_id})
            items = binding._getData(set_id).items()
            items.sort()
            for key, value in items:
                if not hasattr(set_obj, key):
                    continue
                field = binding.getElement(set_id, key).field
                self.startElementNS(namespace, key)
                if not value is None:
                    field.validator.serializeValue(field, value, self)
                self.endElementNS(namespace, key)
            self.endElement('set')
        self.endElement('metadata')

class VersionedContentProducer(SilvaBaseProducer):
    """Base Class for all versioned content
    """
    def workflow(self):
        """Export the XML for the versioning workflow
        """
        if not self.getSettings().workflow():
            return
        self.startElement('workflow')
        version = self.context.get_unapproved_version_data()
        if version[0]:
            self.workflow_version(version, 'unapproved')
        version = self.context.get_approved_version_data()
        if version[0]:
            self.workflow_version(version, 'approved')
        version = self.context.get_public_version_data()
        if version[0]:
            self.workflow_version(version, 'public')
        for version in self.context.get_previous_versions_data():
            self.workflow_version(version, 'closed')
        self.endElement('workflow')

    def workflow_version(self, version, status):
        """Export the XML for the different workflow versions. (Right now:
        Published, Approved, Unapproved, and Closed, but to the XML these
        are arbitrary)
        """
        id, publication_datetime, expiration_datetime = version
        self.startElement('version', {'id':id})
        self.startElement('status')
        self.handler.characters(status)
        self.endElement('status')
        self.startElement('publication_datetime')
        if publication_datetime:
            if type(publication_datetime) == type(DateTime()):
                self.handler.characters(str(publication_datetime.HTML4()))
            else:
                self.handler.characters(unicode(str(publication_datetime)))
        self.endElement('publication_datetime')
        self.startElement('expiration_datetime')
        if expiration_datetime:
            if type(expiration_datetime) == type(DateTime()):
                self.handler.characters(str(expiration_datetime.HTML4()))
            else:
                self.handler.characters(unicode(str(expiration_datetime)))
        self.endElement('expiration_datetime')
        self.endElement('version')

    def versions(self):
        """Export the XML of the versions themselves.
        """
        if self.getSettings().allVersions():
            vm = version_management.getVersionManagementAdapter(self.context)
            for version in vm.getVersions():
                # getVersions will order by id - most recent last.
                self.subsax(version)
        else:
            # XXX handle single version export. Is previewable right? Is
            # there a better method that is guaranteed to return a best
            # guess version?
            self.subsax(self.context.get_previewable())

    def metadata(self):
        """Versioned Content has no metadata, the metadata is all on the
        versions themselves.
        """
        return

class FolderProducer(SilvaBaseProducer):
    """Export a Silva Folder object to XML.
    """
    def sax(self):
        self.startElement('folder', {'id': self.context.id})
        self.metadata()
        self.startElement('content')
        default = self.context.get_default()
        if default is not None:
            self.startElement('default')
            self.subsax(default)
            self.endElement('default')
        for object in self.context.get_ordered_publishables():
            if (IPublication.providedBy(object) and
                    not self.getSettings().withSubPublications()):
                continue
            self.subsax(object)
        for object in self.context.get_assets():
            self.subsax(object)
        if self.getSettings().otherContent():
            for object in self.context.get_other_content():
                self.subsax(object)
        self.endElement('content')
        self.endElement('folder')

class PublicationProducer(SilvaBaseProducer):
    """Export a Silva Publication object to XML.
    """
    def sax(self):
        self.startElement('publication', {'id': self.context.id})
        self.metadata()
        self.startElement('content')
        default = self.context.get_default()
        if default is not None:
            self.startElement('default')
            self.subsax(default)
            self.endElement('default')
        for object in self.context.get_ordered_publishables():
            if (IPublication.providedBy(object) and
                    not self.getSettings().withSubPublications()):
                continue
            self.subsax(object)
        for object in self.context.get_assets():
            self.subsax(object)
        if self.getSettings().otherContent():
            for object in self.context.get_other_content():
                self.subsax(object)
        self.endElement('content')
        self.endElement('publication')

class LinkProducer(VersionedContentProducer):
    """Export a Silva Link object to XML.
    """
    def sax(self):
        self.startElement('link', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElement('link')

class LinkVersionProducer(SilvaBaseProducer):
    """Export a version of a Silva Link object to XML.
    """
    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.metadata()
        self.startElement('url')
        self.handler.characters(self.context.get_url())
        self.endElement('url')
        self.endElement('content')

class GhostProducer(VersionedContentProducer):
    """Export a Silva Ghost object to XML.
    """
    def sax(self):
        self.startElement('ghost', {'id': self.context.id})
        self.workflow()
        self.versions()
        self.endElement('ghost')

class GhostVersionProducer(SilvaBaseProducer):
    """Export a verson of a Silva Ghost object to XML.
    This actually exports the object the ghost refers to, with the ghost id and
    reference added as attributes.
    """
    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        content = self.context.get_haunted_unrestricted()
        if content is not None:
            meta_type = content.meta_type
        else:
            meta_type = ''
        self.startElement('metatype')
        self.handler.characters(meta_type)
        self.endElement('metatype')
        haunted_url = self.context.get_haunted_url()
        self.startElement('haunted_url')
        self.handler.characters(haunted_url)
        self.endElement('haunted_url')
        if content is not None:
            content = content.get_viewable()
            if content is not None:
                self.subsax(content)
        self.endElement('content')

class GhostFolderProducer(SilvaBaseProducer):
    """Export a Silva Ghost Folder object to XML.
    """
    def sax(self):
        self.startElement('ghost_folder', {'id': self.context.id})
        self.startElement('content')
        content = self.context.get_haunted_unrestricted()
        meta_type = content is not None and content.meta_type or "" 
        haunted_url = self.context.get_haunted_url()
        self.startElement('metatype')
        self.handler.characters(meta_type)
        self.endElement('metatype')
        self.startElement('haunted_url')
        self.handler.characters(haunted_url)
        self.endElement('haunted_url')
        self.endElement('content')
        self.endElement('ghost_folder')

class AutoTOCProducer(SilvaBaseProducer):
    """Export an AutoTOC object to XML.
    """
    def sax(self):
        self.startElement('auto_toc', {'id': self.context.id,
                                       'depth': str(self.context.toc_depth()),
                                       'types': ','.join(self.context.get_local_types()),
                                       'sort_order': self.context.sort_order(),
                                       'show_icon': str(self.context.show_icon()),
                                       'display_desc_flag': str(self.context.display_desc_flag())})
        self.metadata()
        self.endElement('auto_toc')
    
class FileProducer(SilvaBaseProducer):
    """Export a File object to XML.
    """
    def sax(self):
        path = self.context.getPhysicalPath()
        self.startElement('file_asset', {'id': self.context.id})
        self.metadata()
        # self.startElement('mime_type')
        # self.handler.characters(self.context.get_mime_type())
        # self.endElement('mime_type')
        self.getInfo().addAssetPath(path)
        self.startElement('asset_id')
        self.handler.characters(self.getInfo().getAssetPathId(path))
        self.endElement('asset_id')
        self.endElement('file_asset')

class ImageProducer(SilvaBaseProducer):
    """Export an Image object to XML.
    """
    def sax(self):
        path = self.context.getPhysicalPath()
        self.startElement('image_asset', {
            'id': self.context.id,
            'web_format': self.context.getWebFormat(),
            'web_scale': self.context.getWebScale(),
            'web_crop': self.context.getWebCrop(),
            })
        self.metadata()
        self.getInfo().addAssetPath(path)
        self.startElement('asset_id')
        self.handler.characters(self.getInfo().getAssetPathId(path))
        self.endElement('asset_id')
        self.endElement('image_asset')

class IndexerProducer(SilvaBaseProducer):
    """Export an IndexerProducer to XML.
    """
    def sax(self):
        self.startElement('indexer', {'id': self.context.id})
        self.metadata()
        self.endElement('indexer')

class ZexpProducer(SilvaBaseProducer):
    """Export any unknown content type to a zexp in the zip-file.
    """
    def sax(self):
        info = self.getInfo()
        if (info is not None) and (self.context is not None):
            path = self.context.getPhysicalPath()
            id = self.context.id
            if callable(id):
                id = id()
            self.startElement('unknown_content', {'id': id})
            info.addZexpPath(path)
            path_id = self.getInfo().getZexpPathId(path)
            self.startElement('zexp_id')
            self.handler.characters(path_id)
            self.endElement('zexp_id')
            self.endElement('unknown_content')
    
class SilvaExportRoot:
    def __init__(self, exportable):
        self._exportable = exportable
        self._exportDateTime = DateTime()

    def getSilvaProductVersion(self):
        return 'Silva %s' % self._exportable.get_root().get_silva_software_version()
    
    def getExportable(self):
        return self._exportable
    
    def getDateTime(self):
        return self._exportDateTime
        
class SilvaExportRootProducer(xmlexport.BaseProducer):
    def sax(self):
        self.startElement(
            'silva',
            {'datetime': self.context.getDateTime().HTML4(),
             'path': '/'.join(self.context.getExportable().getPhysicalPath()),
             'url': self.context.getExportable().absolute_url(),
             'silva_version': self.context.getSilvaProductVersion()})
        self.subsax(self.context.getExportable())
        self.endElement('silva')
        
class ExportSettings(xmlexport.BaseSettings):
    def __init__(self, asDocument=True, outputEncoding='utf-8',
                 workflow=True, allVersions=True,
                 withSubPublications=True, otherContent=True):
        xmlexport.BaseSettings.__init__(self, asDocument, outputEncoding)
        self._workflow = workflow
        self._all_versions = allVersions
        self._with_sub_publications = withSubPublications
        self._other_content = otherContent
        self._render_external = False
        
    def setWithSubPublications(self, with_sub_publications):
        self._with_sub_publications = with_sub_publications
        
    def setLastVersion(self, last_version):
        self._all_versions = not last_version

    def setExternalRendering(self, external_rendering):
        self._render_external = external_rendering
        
        #     def setFullMedia():
        #         self._fullmedia = 1
        
        #     def fullMediaExport():
        #         return self._fullmedia
        
    def workflow(self):
        return self._workflow

    def allVersions(self):
        return self._all_versions

    def withSubPublications(self):
        return self._with_sub_publications

    def otherContent(self):
        return self._other_content

    def externalRendering(self):
        return self._render_external
    
class ExportInfo:
    def __init__(self):
        self._asset_paths = {}
        self._zexp_paths = {}
        self._last_asset_id = 0
        self._last_zexp_id = 0
        
    def addAssetPath(self, path):
        self._asset_paths[path] = self._makeUniqueAssetId(path)
    
    def getAssetPathId(self, path):
        return self._asset_paths[path]

    def getAssetPaths(self):
        return self._asset_paths.items()
    
    def _makeUniqueAssetId(self, path):
        ext = ''
        name = path[-1]
        if len(name) > 4:
            if name[-4] == '.':
                ext = name[-4:]
        self._last_asset_id += 1
        return str(self._last_asset_id) + ext
    
    def addZexpPath(self, path):
        self._zexp_paths[path] = self._makeUniqueZexpId(path)
    
    def getZexpPathId(self, path):
        return self._zexp_paths[path]

    def getZexpPaths(self):
        return self._zexp_paths.items()
    
    def _makeUniqueZexpId(self, path):
        self._last_zexp_id += 1
        return str(self._last_zexp_id) + '.zexp'
