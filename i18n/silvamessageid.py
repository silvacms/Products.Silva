from Products.PlacelessTranslationService.MessageID import MessageIDFactory
from Products.PlacelessTranslationService.MessageID import MessageIDUnicode

from Products.PlacelessTranslationService import translate, utranslate

try:
    from Globals import get_request
except ImportError:
    from PatchStringIO import applyRequestPatch
    applyRequestPatch()

class SilvaMessageIDUnicode(MessageIDUnicode):
    """
    """
    __allow_access_to_unprotected_subobjects__ = 1
    
    def set_mapping(self, mapping):
        """Set a mapping for message interpolation
        """
        self.mapping = mapping

    # XXX *sigh* we override the translate method on the MessageIDUnicode
    # base class, because not passing a context will eventually trigger
    # a log entry for all translated strings in a request.
    def translate(self):
        """translate the message id
        """
        return utranslate(
            domain=self.domain, msgid=self.ustr, mapping=self.mapping,
            context=get_request(), default=self.default)
        
def SilvaMessageIDFactory(ustr, domain='silva'):
    return SilvaMessageIDUnicode(ustr, domain)
