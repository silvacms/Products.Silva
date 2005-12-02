"""Provides a function called 'translate' that *must* be imported as '_':

    from Products.Silva.i18n import translate as _

and will provide, if PlacelessTranslationService is installed, a 
MessageIDFactory that returns MessageIDs for i18n'ing Product code 
and Python scripts.
"""
from zope.i18nmessageid import MessageIDFactory

translate = MessageIDFactory('silva')
