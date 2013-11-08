# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.cachedescriptors.property import Lazy
from zeam.component import getComponent

from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.interfaces.events import IContentImported
from silva.core.services.interfaces import ICataloging
from silva.core.xml import NS_SILVA_URI, handlers
from silva.translations import translate as _

silvaconf.namespace(NS_SILVA_URI)


@grok.subscribe(interfaces.ISilvaObject, IContentImported)
def reindex_import_content(content, event):
    """Re-index imported content.
    """
    ICataloging(content).index()


@grok.subscribe(interfaces.IQuotaObject, IContentImported)
def update_quota_import_content(content, event):
    """Update the quota of imported content (to be sure).
    """
    content.update_quota()


class FolderHandler(handlers.SilvaContainerHandler):
    grok.name('folder')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addFolder(identifier, '', no_default_content=True)

    def _verifyContent(self, content):
        return interfaces.IFolder.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'folder'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'folder'):
            self.storeMetadata()
            self.notifyImport()


class PublicationHandler(handlers.SilvaContainerHandler):
    grok.name('publication')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addPublication(identifier, '', no_default_content=True)

    def _verifyContent(self, content):
        return interfaces.IPublication.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'publication'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'publication'):
            self.storeMetadata()
            self.notifyImport()


class AutoTOCHandler(handlers.SilvaHandler):
    grok.name('auto_toc')

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addAutoTOC(identifier, '')

    def _verifyContent(self, content):
        return interfaces.IAutoTOC.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'auto_toc'):
            toc = self.createContent(attrs)
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

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addIndexer(identifier, '')

    def _verifyContent(self, content):
        return interfaces.IIndexer.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'indexer'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'indexer'):
            #self.setMaintitle()
            self.storeMetadata()
            self.getExtra().addAction(self.result().update, [])
            self.notifyImport()


class GhostHandler(handlers.SilvaHandler):
    grok.name('ghost')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): GhostVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addGhost(identifier, None, no_default_version=True)

    def _verifyContent(self, content):
        return interfaces.IGhost.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'ghost'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'ghost'):
            self.notifyImport()


class GhostVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'haunted'):
                self.handlerFactories.contentHandler('haunted'),}

    @Lazy
    def _getManager(self):
        return getComponent((interfaces.IGhost,), interfaces.IGhostManager)

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addGhostVersion(identifier, None)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            self.createVersion(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            importer = self.getExtra()
            version = self.result()
            haunted = self.getData('haunted')
            if not haunted:
                importer.reportProblem(_(u'Missing ghost target.'), version)
            else:

                def set_target(target):
                    problem = self._getManager(
                        ghost=version.get_silva_object()).validate(target)
                    if problem is not None:
                        importer.reportProblem(problem.doc(), version)
                    else:
                        version.set_haunted(target)

                importer.resolveImportedPath(version, set_target, haunted)
            self.updateVersionCount()
            self.storeWorkflow()


class GhostFolderHandler(handlers.SilvaContainerHandler):
    grok.name('ghost_folder')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'haunted'):
                self.handlerFactories.contentHandler('haunted'),}
    @Lazy
    def _getManager(self):
        return getComponent(
            (interfaces.IGhostFolder,), interfaces.IGhostManager)

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addGhostFolder(identifier, None, no_default_content=True)

    def _verifyContent(self, content):
        return interfaces.IGhostFolder.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'ghost_folder'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'ghost_folder'):
            folder = self.result()
            haunted = self.getData('haunted')
            importer = self.getExtra()
            if haunted is None:
                importer.reportProblem(u'Missing ghost folder target.', folder)
            else:

                def set_target(target):
                    problem = self._getManager(ghost=folder).validate(target)
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

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addLink(identifier, '', no_default_version=True)

    def _verifyContent(self, content):
        return interfaces.ILink.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'link'):
            self.createContent(attrs)

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

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addLinkVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            self.createVersion(attrs)

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

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addImage(identifier, '', None)

    def _verifyContent(self, content):
        return interfaces.IImage.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'image'):
            self.createContent(attrs)
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

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addFile(identifier, '', None)

    def _verifyContent(self, content):
        return interfaces.IFile.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'file'):
            self.createContent(attrs)

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


class GhostAssetHandler(handlers.SilvaHandler):
    grok.name('ghost_asset')

    def getOverrides(self):
        return {
            (NS_SILVA_URI, 'haunted'):
                self.handlerFactories.contentHandler('haunted'),}

    @Lazy
    def _getManager(self):
        return getComponent((interfaces.IGhostAsset,), interfaces.IGhostManager)

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['Silva']
        factory.manage_addGhostAsset(identifier, None)

    def _verifyContent(self, content):
        return interfaces.IGhostAsset.providedBy(content)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'ghost_asset'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'ghost_asset'):
            importer = self.getExtra()
            asset = self.result()
            haunted = self.getData('haunted')
            if not haunted:
                importer.reportProblem(_(u'Missing ghost target.'), asset)
            else:

                def set_target(target):
                    problem = self._getManager(ghost=asset).validate(target)
                    if problem is not None:
                        importer.reportProblem(problem.doc(), asset)
                    else:
                        asset.set_haunted(target)

                importer.resolveImportedPath(asset, set_target, haunted)
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
            # XXX check name
            identifier = self.getData('id')
            import_file = extra.getFile('zexps/' + self.getData('zexp'))
            content = extra.root._p_jar.importFile(import_file)
            self.parent()._setObject(identifier, content)
            self.setResultId(identifier)
            self.notifyImport()





