# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.traversing.browser import absoluteURL
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from AccessControl.security import checkPermission

from silva.core.interfaces import IIndexer
from silva.core.smi.content import IEditScreen
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms


class IndexerAddForm(silvaforms.SMIAddForm):
    """Add form for Silva indexer.
    """
    grok.context(IIndexer)
    grok.name(u"Silva Indexer")


class IndexerEditForm(silvaforms.SMIForm):
    """Edit form for an indexer. There is not that much to edit however.
    """
    grok.context(IIndexer)
    grok.require('silva.ReadSilvaContent')
    grok.implements(IEditScreen)

    label = _("Update Silva Indexer")
    description = _(
        u"An index is not editable. "
        u"However, you can update the index to include recent added content.")
    actions = silvaforms.Actions(silvaforms.CancelEditAction())

    def update_index_available(self):
        return checkPermission('silva.ChangeSilvaContent', self.context)

    @silvaforms.action(
        _(u"Update index"),
        accesskey=u"u",
        available=update_index_available,
        description=_(u"Update index to include recent added content"))
    def update_index(self):
        self.context.update()
        notify(ObjectModifiedEvent(self.context))
        self.send_message(
            _(u"Index content have been successfully updated."),
            type="feedback")


class IndexerView(silvaviews.View):
    """View on indexer objects.
    """
    grok.context(IIndexer)

    def links(self, links):
        for title, content, name in links:
            if content is not None:
                url = absoluteURL(content, self.request)
            else:
                url = ""
            yield '<a class="indexer" href="%s#%s">%s</a>' % (url, name, title)


