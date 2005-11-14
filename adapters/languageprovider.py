
from DateTime import DateTime
# Zope
from zope.interface import implements
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo

from Products.Silva.interfaces import ISilvaObject
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces
from Products.Silva import SilvaPermissions
try:
   from Products import PlacelessTranslationService
   PTS_AVAILABLE = True
except ImportError:
   PTS_AVAILABLE = False

class PTSLanguageProvider(adapter.Adapter):
    """
    """
    implements(interfaces.ILanguageProvider)

    security = ClassSecurityInfo()
    security.declareObjectProtected(SilvaPermissions.ReadSilvaContent)

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        return PlacelessTranslationService.getLanguages(domain='silva')

    security.declarePublic('setPreferredLanguage')
    def setPreferredLanguage(self, language):
        path = '/'.join(
            self.context.get_publication().get_root().getPhysicalPath())
        self.context.REQUEST.RESPONSE.setCookie(
            'pts_language', language, 
            path=path, expires=(DateTime()+365).rfc822())

    security.declarePublic('getPreferredLanguage')
    def getPreferredLanguage(self):
        return PlacelessTranslationService.negotiator.negotiate(
            self.getAvailableLanguages(), self.context.REQUEST, 'language')

Globals.InitializeClass(PTSLanguageProvider)

class DummyLanguageProvider(adapter.Adapter):
    security = ClassSecurityInfo()
    security.declareObjectProtected(SilvaPermissions.ReadSilvaContent)

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        return ['en']

    security.declarePublic('setPreferredLanguage')
    def setPreferredLanguage(self, language):
        pass

    security.declarePublic('getPreferredLanguage')
    def getPreferredLanguage(self):
        return 'en'

Globals.InitializeClass(DummyLanguageProvider)

def getLanguageProvider(context):
    if PTS_AVAILABLE:
        return PTSLanguageProvider(context).__of__(context)

    return DummyLanguageProvider(context).__of__(context)
