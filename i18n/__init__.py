"""Provides a function called 'translate' that *must* be imported as '_':

    from Products.Silva.i18n import translate as _

    and will provide, if PlacelessTranslationService is installed, a 
    MessageIDFactory that returns MessageIDs for i18n'ing Product code 
    and Python scripts.

    If PlacelessTranslationService is not installed, it will return a
    'dummy' object that provides the MessageID interface but doesn't
    translate strings (it just returns what comes in, optionally interpolating
    values)
"""

try:
    from silvamessageid import SilvaMessageIDFactory as translate
except ImportError:
    from dummymessageid import DummyMessageIDFactory as translate
