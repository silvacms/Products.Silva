# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from Products.Silva.Ghost import validate_target
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.interfaces.events import IContentImported
from silva.core.services.interfaces import ICataloging
from silva.core.xml import NS_SILVA_URI, handlers
from silva.translations import translate as _

silvaconf.namespace(NS_SILVA_URI)


@grok.subscribe(ISilvaObject, IContentImported)
def reindex_import_content(content, event):
    """Re-index imported content.
    """
    ICataloging(content).index()


class SilvaExportRootHandler(handlers.SilvaHandler):
    grok.name('silva')

    def getResultPhysicalPath(self):
        return []

    def getOriginalPhysicalPath(self):
        return []


class FolderHandler(handlers.SilvaHandler):
    grok.name('folder')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'folder'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addFolder(identifier, '', no_default_content=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'folder'):
            self.storeMetadata()
            self.notifyImport()


class PublicationHandler(handlers.SilvaHandler):
    grok.name('publication')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'publication'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addPublication(
                identifier, '', no_default_content=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'publication'):
            self.storeMetadata()
            self.notifyImport()


class AutoTOCHandler(handlers.SilvaHandler):
    grok.name('auto_toc')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'auto_toc'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addAutoTOC(identifier, '')
            toc = self.setResultId(identifier)
            #not all imported TOCs will have these, so only set if they do
            if (attrs.get((None,'depth'),None)):
                toc.set_toc_depth(int(attrs[(None,'depth')]))
            if (attrs.get((None,'types'),None)):
                toc.set_local_types(attrs[(None, 'types')].split(','))
            if (attrs.get((None,'display_desc_flag'),None)):
                toc.set_display_desc_flag(attrs[(None,'display_desc_flag')]=='True')
            if (attrs.get((None,'show_icon'),None)):
                toc.set_show_icon(attrs[(None,'show_icon')]=='True')
            if (attrs.get((None,'sort_order'),None)):
                toc.set_sort_order(attrs[(None,'sort_order')])

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'auto_toc'):
            self.storeMetadata()
            self.notifyImport()


class IndexerHandler(handlers.SilvaHandler):
    grok.name('indexer')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'indexer'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addIndexer(identifier, '')
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'indexer'):
            #self.setMaintitle()
            self.storeMetadata()
            self.getExtra().addAction(self.result().update, [])
            self.notifyImport()


class VersionHandler(handlers.SilvaHandler):
    grok.name('version')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'status'):
                self.handlerFactories.contentHandler('status'),
            (NS_SILVA_URI, 'publication_datetime'):
                self.handlerFactories.contentHandler('publication_datetime'),
            (NS_SILVA_URI, 'expiration_datetime'):
                self.handlerFactories.contentHandler('expiration_datetime'),
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'version'):
            self.setData('id', attrs[(None, 'id')])

    def endElementNS(self, name, qname):
        self.setWorkflowVersion(
            self.getData('id'),
            self.getData('publication_datetime'),
            self.getData('expiration_datetime'),
            self.getData('status'))


class MetadataSetHandler(handlers.SilvaHandler):
    grok.name('set')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'set'):
            self.parentHandler().setMetadataSet(attrs[(None, 'id')])
        elif name != (NS_SILVA_URI, 'value'):
            self.parentHandler().setMetadataKey(name[1])
        else:
            self.parentHandler().setMetadataMultiValue(True)
        self.setResult(None)

    def characters(self, chars):
        if self.parentHandler().metadataKey() is not None:
            self._chars = chars.strip()

    def endElementNS(self, name, qname):
        if name != (NS_SILVA_URI, 'set'):
            value = getattr(self, '_chars', None)

            if self.parentHandler().metadataKey() is not None:
                self.parentHandler().setMetadata(
                    self.parentHandler().metadataSet(),
                    self.parentHandler().metadataKey(),
                    value)
        if name != (NS_SILVA_URI, 'value'):
            self.parentHandler().setMetadataKey(None)
            self.parentHandler().setMetadataMultiValue(False)
        self._chars = None


class GhostHandler(handlers.SilvaHandler):
    grok.name('ghost')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): GhostVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'ghost'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addGhost(identifier, None, no_default_version=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'ghost'):
            self.notifyImport()


class GhostVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'haunted'):
                self.handlerFactories.contentHandler('haunted'),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                uid = attrs[(None, 'version_id')].encode('utf8')
                factory = self.parent().manage_addProduct['Silva']
                factory.manage_addGhostVersion(uid, None)
                self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            importer = self.getExtra()
            ghost = self.result()
            haunted = self.getData('haunted')
            if not haunted:
                importer.reportProblem(_(u'Missing ghost target.'), ghost)
            else:

                def set_target(target):
                    problem = validate_target(ghost, target)
                    if problem is not None:
                        importer.reportProblem(problem.doc(), ghost)
                    else:
                        ghost.set_haunted(target)

                importer.resolveImportedPath(ghost, set_target, haunted)
            self.updateVersionCount()
            self.storeWorkflow()


class GhostFolderHandler(handlers.SilvaHandler):
    grok.name('ghost_folder')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'haunted'):
                self.handlerFactories.contentHandler('haunted'),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'ghost_folder'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addGhostFolder(
                identifier, None, no_default_content=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'ghost_folder'):
            folder = self.result()
            haunted = self.getData('haunted')
            importer = self.getExtra()
            if haunted is None:
                importer.reportProblem(u'Missing ghost folder target.', folder)
            else:

                def set_target(target):
                    problem = validate_target(folder, target, is_folderish=True)
                    if problem is not None:
                        importer.reportProblem(problem.doc(), folder)
                    else:
                        folder.set_haunted(target)
                        folder.haunt()

                importer.resolveImportedPath(folder, set_target, haunted)
            self.notifyImport()


class LinkHandler(handlers.SilvaHandler):
    grok.name('link')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): LinkVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'link'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addLink(identifier, '', no_default_version=True)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'link'):
            self.notifyImport()


class LinkVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'url'):
                self.handlerFactories.contentHandler('url'),
            (NS_SILVA_URI, 'target'):
                self.handlerFactories.contentHandler('target'),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                uid = attrs[(None, 'version_id')].encode('utf8')
                factory = self.parent().manage_addProduct['Silva']
                factory.manage_addLinkVersion(uid, '')
                self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            link = self.result()
            url = self.getData('url')
            if url is not None:
                link.set_relative(False)
                link.set_url(url)
            else:
                link.set_relative(True)
                importer = self.getExtra()
                target = self.getData('target')
                if not target:
                    importer.reportProblem('Missing relative link target.', link)
                else:
                    importer.resolveImportedPath(link, link.set_target, target)
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class ImageHandler(handlers.SilvaHandler):
    """Import a Silva image.
    """
    grok.name('image')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'asset'):
                self.handlerFactories.tagHandler('asset')}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'image'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addImage(identifier, '', None)
            self.setResultId(identifier)
            self.setData('web_format', attrs.get((None, 'web_format')))
            self.setData('web_scale', attrs.get((None, 'web_scale')))
            self.setData('web_crop', attrs.get((None, 'web_crop')))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'image'):
            importer = self.getExtra()
            image = self.result()
            asset_filename = 'assets/' + self.getData('asset')
            image_payload = importer.getFile(asset_filename)
            if image_payload is None:
                importer.reportProblem(
                    "Missing image file in the import: {0}.".format(
                        asset_filename),
                    image)
            else:
                image.set_image(image_payload)

            web_format = self.getData('web_format')
            web_scale = self.getData('web_scale')
            web_crop = self.getData('web_crop')
            if web_format or web_scale or web_crop:
                image.set_web_presentation_properties(
                    web_format, web_scale, web_crop)

            self.storeMetadata()
            self.notifyImport()


class FileHandler(handlers.SilvaHandler):
    """Import a Silva File.
    """
    grok.name('file')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'asset'):
                self.handlerFactories.tagHandler('asset')}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'file'):
            identifier = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['Silva']
            factory.manage_addFile(identifier, '', None)
            self.setResultId(identifier)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'file'):
            filename = self.getData('asset')
            importer = self.getExtra()
            file_asset = self.result()
            file_payload = importer.getFile('assets/' + filename)
            if file_payload is None:
                importer.reportProblem("Missing file content.", file_asset)
            else:
                file_asset.set_file(file_payload)
            self.storeMetadata()
            self.notifyImport()


class UnknownContentHandler(handlers.SilvaHandler):
    """Importer for content which have been exported in a ZEXP.
    """
    grok.name('unknown_content')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'zexp'):
                self.handlerFactories.tagHandler('zexp')}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'unknown_content'):
            self.setData('id', self.generateIdentifier(attrs))

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'unknown_content'):
            extra = self.getExtra()
            # XXX check non
            identifier = self.getData('id')
            import_file = extra.getFile('zexps/' + self.getData('zexp'))
            content = extra.root._p_jar.importFile(import_file)
            self.parent()._setObject(identifier, content)
            self.setResultId(identifier)
            self.notifyImport()





