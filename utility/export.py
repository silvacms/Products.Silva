
from grokcore.component import implements, GlobalUtility

from zope.component import getAdapter, getAdapters
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from Products.Silva.adapters.interfaces import IContentExporter, IDefaultContentExporter
from Products.Silva.utility.interfaces import IExportUtility

class ExportUtility(GlobalUtility):
    """Utility to manage export.
    """

    implements(IExportUtility)

    def createContentExporter(self, context, name):
        """Create a content exporter.
        """
        return getAdapter(context, IContentExporter, name=name)

    def listContentExporter(self, context):
        """List available exporter.
        """

        default = None
        all = []
        for adapter in getAdapters((context,), IContentExporter):
            term = SimpleTerm(value=adapter[0], title=adapter[1].name)
            if IDefaultContentExporter.providedBy(adapter[1]):
                if not default:
                    default = term
                else:
                    assert "There is two default content exporter"
            else:
                all.append(term)
        return SimpleVocabulary([default,] + all)

