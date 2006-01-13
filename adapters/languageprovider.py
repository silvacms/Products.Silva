from DateTime import DateTime
# Zope
from zope.interface import implements
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo, allow_module

from Products.Silva.interfaces import ISilvaObject
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces
from Products.Silva import SilvaPermissions

from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages
from zope.app import zapi
from zope.publisher.browser import BrowserLanguages

# this isn't a real z3 adapter yet as it's used by view code
class LanguageProvider(adapter.Adapter):
    """
    """
    implements(interfaces.ILanguageProvider)

    security = ClassSecurityInfo()
    security.declareObjectProtected(SilvaPermissions.ReadSilvaContent)

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        silva_domain = zapi.getUtility(ITranslationDomain, 'silva')
        # XXX awful hack, but we don't have access to any
        # 'getAvailableLanguages' functionality apparently..
        return silva_domain._catalogs.keys()

    security.declarePublic('setPreferredLanguage')
    def setPreferredLanguage(self, language):
        path = '/'.join(
            self.context.get_publication().get_root().getPhysicalPath())
        self.context.REQUEST.RESPONSE.setCookie(
            'silva_language', language, 
            path=path, expires=(DateTime()+365).rfc822())
    
    security.declarePublic('getPreferredLanguage')
    def getPreferredLanguage(self):
        return IUserPreferredLanguages(
            self.context.REQUEST).getPreferredLanguages()[0]

Globals.InitializeClass(LanguageProvider)

# somehow we could access this from a python script before, but
# not anymore.. Add in some voodoo code to make it possible again
__allow_access_to_unprotected_subobjects__ = True

module_security = ModuleSecurityInfo(
    'Products.Silva.adapters.languageprovider')

module_security.declareProtected(
    SilvaPermissions.ReadSilvaContent, 'getLanguageProvider')

def getLanguageProvider(context):
    return LanguageProvider(context).__of__(context)

# new language extractor that looks in the silva_language cookie first,
# then fall back on browser setting
class SilvaLanguages(BrowserLanguages):
    def getPreferredLanguages(self):
        languages = super(
            SilvaLanguages, self).getPreferredLanguages()
        cookie_language = self.request.cookies.get('silva_language')
        if cookie_language is not None:
            languages = [cookie_language] + languages
        return languages
