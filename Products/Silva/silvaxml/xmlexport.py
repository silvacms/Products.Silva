# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface
from five import grok
from silva.core import interfaces
from silva.core.xml import producers


class FolderProducer(producers.SilvaContainerProducer):
    """Export a Silva Folder object to XML.
    """
    grok.adapts(interfaces.IFolder, Interface)

    def sax(self):
        self.startElement('folder', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElement('folder')


class PublicationProducer(producers.SilvaContainerProducer):
    """Export a Silva Publication object to XML.
    """
    grok.adapts(interfaces.IPublication, Interface)

    def sax(self):
        self.startElement('publication', {'id': self.context.id})
        self.sax_metadata()
        self.sax_contents()
        self.endElement('publication')


class LinkProducer(producers.SilvaVersionedContentProducer):
    """Export a Silva Link object to XML.
    """
    grok.adapts(interfaces.ILink, Interface)

    def sax(self):
        self.startElement('link', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElement('link')


class LinkVersionProducer(producers.SilvaProducer):
    """Export a version of a Silva Link object to XML.
    """
    grok.adapts(interfaces.ILinkVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.sax_metadata()
        if self.context.get_relative():
            tag = 'target'
            if self.getOptions().external_rendering:
                tag = 'url'
            self.startElement(tag)
            self.characters(self.get_reference(u'link'))
            self.endElement(tag)
        else:
            self.startElement('url')
            self.characters(self.context.get_url())
            self.endElement('url')
        self.endElement('content')


class GhostProducer(producers.SilvaVersionedContentProducer):
    """Export a Silva Ghost object to XML.
    """
    grok.adapts(interfaces.IGhost, Interface)

    def sax(self):
        self.startElement('ghost', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElement('ghost')


class GhostVersionProducer(producers.SilvaProducer):
    """Export a verson of a Silva Ghost object to XML.
    This actually exports the object the ghost refers to, with the ghost id and
    reference added as attributes.
    """
    grok.adapts(interfaces.IGhostVersion, Interface)

    def sax(self):
        self.startElement('content', {'version_id': self.context.id})
        self.startElement('haunted')
        self.characters(self.get_reference(u'haunted'))
        self.endElement('haunted')
        if self.getOptions().external_rendering:
            # Include an export of the haunted object, for external
            # rendering.
            haunted = self.context.get_haunted()
            if haunted is not None:
                content = haunted.get_viewable()
                if content is not None:
                    self.subsax(content)
        self.endElement('content')


class GhostFolderProducer(producers.SilvaProducer):
    """Export a Silva Ghost Folder object to XML.
    """
    grok.adapts(interfaces.IGhostFolder, Interface)

    def sax(self):
        self.startElement('ghost_folder', {'id': self.context.id})
        self.startElement('content')
        self.startElement('haunted')
        self.characters(self.get_reference(u'haunted'))
        self.endElement('haunted')
        self.endElement('content')
        self.endElement('ghost_folder')


class AutoTOCProducer(producers.SilvaProducer):
    """Export an AutoTOC object to XML.
    """
    grok.adapts(interfaces.IAutoTOC, Interface)

    def sax(self):
        self.startElement(
            'auto_toc',
            {'id': self.context.id,
             'depth': str(self.context.get_toc_depth()),
             'types': ','.join(self.context.get_local_types()),
             'sort_order': self.context.get_sort_order(),
             'show_icon': str(self.context.get_show_icon()),
             'display_desc_flag': str(self.context.get_display_desc_flag())})
        self.sax_metadata()
        self.endElement('auto_toc')


class FileProducer(producers.SilvaProducer):
    """Export a File object to XML.
    """
    grok.adapts(interfaces.IFile, Interface)

    def sax(self):
        path = self.context.getPhysicalPath()
        identifier = self.getExported().addAssetPath(path)
        self.startElement('file', {'id': self.context.id})
        self.sax_metadata()
        self.startElement('asset', {'id': identifier})
        self.endElement('asset')
        self.endElement('file')


class ImageProducer(producers.SilvaProducer):
    """Export an Image object to XML.
    """
    grok.adapts(interfaces.IImage, Interface)

    def sax(self):
        path = self.context.getPhysicalPath()
        identifier = self.getExported().addAssetPath(path)
        self.startElement('image', {
            'id': self.context.id,
            'web_format': self.context.get_web_format(),
            'web_scale': self.context.get_web_scale(),
            'web_crop': self.context.get_web_crop(),
            })
        self.sax_metadata()
        self.startElement('asset', {'id': identifier})
        self.endElement('asset')
        self.endElement('image')


class GhostAssetProducer(producers.SilvaProducer):
    """Export a verson of a Silva Asset to XML.
    """
    grok.adapts(interfaces.IGhostAsset, Interface)

    def sax(self):
        self.startElement('ghost_asset', {'id': self.context.id})
        self.startElement('haunted')
        self.characters(self.get_reference(u'haunted'))
        self.endElement('haunted')
        self.endElement('ghost_asset')


class IndexerProducer(producers.SilvaProducer):
    """Export an IndexerProducer to XML.
    """
    grok.adapts(interfaces.IIndexer, Interface)

    def sax(self):
        self.startElement('indexer', {'id': self.context.id})
        self.sax_metadata()
        self.endElement('indexer')



