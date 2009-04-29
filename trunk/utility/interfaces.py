"""Generic utility for Silva
"""

from zope.interface import Interface


class IExportUtility(Interface):
    """Utility to manage export features.
    """

    def createContentExporter(context, name):
        """Create the given exporter.
        """

    def listContentExporter(context):
        """List available exporter for this context.
        """
