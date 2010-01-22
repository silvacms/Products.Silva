# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from silva.core import interfaces
from zExceptions import NotFound
from zope.traversing.browser import absoluteURL


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
        context = self.context
        ms = context.service_metadata
        date_updated = ms.getMetadataValue(
            self.context, 'silva-extra', 'creationtime')
        provider = interfaces.IFeedEntryProvider(self.context.aq_inner)
        for entry in provider.entries():
            entry_updated = entry.date_updated()
            entries.append((entry_updated, entry))
            if entry_updated > date_updated:
                date_updated = entry_updated
        entries.sort()
        feed = [entry[1] for entry in entries]
        url = absoluteURL(context, self.request)
        self.data = {
            'id': url,
            'title': context.get_title(),
            'description': ms.getMetadataValue(
                self.context, 'silva-extra', 'content_description'),
            'url': url,
            'authors': [ms.getMetadataValue(
                self.context, 'silva-extra', 'creator')],
            'date_updated': date_updated,
            'entries': feed}

        self.response.setHeader(
            'Content-Type', 'text/xml;charset=UTF-8')


class RSSFeed(FeedBase):
    """Export the feed as an RSS feed.
    """
    grok.name('rss.xml')
    grok.template('rss')
    grok.context(interfaces.IContainer)


class AtomFeed(FeedBase):
    """Export the feed as an Atom feed.
    """
    grok.name('atom.xml')
    grok.template('atom')
    grok.context(interfaces.IContainer)

