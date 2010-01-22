# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope import component
from zope.traversing.browser import absoluteURL

from Products.SilvaMetadata.interfaces import IMetadataService
from zExceptions import NotFound

from silva.core import interfaces


class ContainerFeedProvider(grok.Adapter):
    """This default feed provider provides feed the immediate content
    of a container.
    """
    grok.context(interfaces.IContainer)
    grok.provides(interfaces.IFeedEntryProvider)
    grok.implements(interfaces.IFeedEntryProvider)

    def entries(self):
        for item in self.context.get_ordered_publishables():
            if not item.is_published():
                continue
            entry = interfaces.IFeedEntry(item, None)
            if entry is not None:
                yield entry


class FeedBase(grok.View):
    """Base class for feed representation.
    """
    grok.baseclass()
    grok.require('zope2.View')

    def update(self):
        if not self.context.allow_feeds():
            raise NotFound()

        entries = []
        service_metadata = component.getUtility(IMetadataService)
        metadata = service_metadata.getMetadata(self.context)
        date_updated = metadata.get('silva-extra', 'creationtime')

        provider = interfaces.IFeedEntryProvider(self.context.aq_inner)
        for entry in provider.entries():
            entry_updated = entry.date_published()
            entries.append((entry_updated.asdatetime(), entry))

        entries.sort(key=lambda x: x[0], reverse=True)
        feed = [entry[1] for entry in entries]

        last_published = feed[0].date_published()
        if  last_published> date_updated:
            date_updated = last_published

        self.data = {
            'title': self.context.get_title(),
            'description': metadata.get('silva-extra', 'content_description'),
            'url': absoluteURL(self.context, self.request),
            'authors': [metadata.get('silva-extra', 'creator')],
            'date_updated': date_updated,
            'entries': feed}

        self.response.setHeader(
            'Content-Type', 'text/xml;charset=UTF-8')


class RSS(FeedBase):
    """Export the feed as an RSS 1.0 feed.
    """
    grok.name('rss.xml')
    grok.context(interfaces.IContainer)


class Atom(FeedBase):
    """Export the feed as an Atom feed.
    """
    grok.name('atom.xml')
    grok.context(interfaces.IContainer)

