# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zExceptions import NotFound
from silva.core.interfaces import IFeedEntry
from Products.Five import BrowserView

class ContainerFeedView(BrowserView):
    """Base class for feed representation."""

    def __call__(self):
        if not self.context.allow_feeds():
            raise NotFound()
        self.request.RESPONSE.setHeader(
            'Content-Type', 'text/xml;charset=UTF-8')
        return super(ContainerFeedView, self).__call__(self)

    def get_data(self):
        """ prepare the data needed by a feed
        """
        entries = []
        context = self.context
        ms = context.service_metadata
        date_updated = ms.getMetadataValue(
            self.context, 'silva-extra', 'creationtime')
        for item in context.get_ordered_publishables():
            if not item.is_published():
                continue
            entry = IFeedEntry(item, None)
            if not entry is None:
                entry_updated = entry.date_updated()
                entries.append((entry_updated, entry))
                if entry_updated > date_updated:
                    date_updated = entry_updated
        entries.sort()
        feed = [entry[1] for entry in entries]
        url = context.absolute_url()
        return {
            'id': url,
            'title': context.get_title(),
            'description': ms.getMetadataValue(
                self.context, 'silva-extra', 'content_description'),
            'url': url,
            'authors': [ms.getMetadataValue(
                self.context, 'silva-extra', 'creator')],
            'date_updated': date_updated,
            'entries': feed
            }
