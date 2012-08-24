
from five import grok
from zope.traversing.browser import absoluteURL
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from AccessControl.security import checkPermission

from silva.core.interfaces import IIndexer
from silva.core.references.interfaces import IReferenceService
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

    def update(self):
        cache = {}
        references = getUtility(IReferenceService).references

        def resolver(cid):
            if cid in cache:
                return cache[cid]
            reference = references.get(cid, None)
            if reference is not None:
                url = absoluteURL(reference.target, self.request)
                cache[cid] = url
                return url
            return ''

        self.__resolver = resolver

    def links(self, links):
        for title, cid, name in links:
            url = self.__resolver(cid)
            yield '<a class="indexer" href="%s#%s">%s</a>' % (url, name, title)


