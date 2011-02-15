"""Custom Exceptions for Silva, raised by the core so that public layouts
   can attach custom error pages"""

from zope.interface import implements

from silva.core.interfaces import INotViewable

class NotViewable(Exception):
    """this exception is raised when a silva object has no published / viewable
       content"""
    implements(INotViewable)