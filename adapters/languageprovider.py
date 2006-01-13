from DateTime import DateTime
# Zope
from zope.interface import implements
import Globals
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo, allow_module

from Products.Silva.interfaces import ISilvaObject
from Products.Silva.adapters import adapter
from Products.Silva.adapters import interfaces
from Products.Silva import SilvaPermissions

from Products.Silva.i18n import translate as _

from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages
from zope.app import zapi
from zope.publisher.browser import BrowserLanguages

# XXX this isn't a real z3 adapter yet as it's used by view code
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

    security.declarePublic('getLanguageName')
    def getLanguageName(self, language_id):
        """Get the name of the language, in the current language.
        """
        self._setupLocale()
        name = self.context.REQUEST.locale.displayNames.languages.get(
            language_id)
        if name is None:
            # if for some reason the language name is unknown, show id
            name = language_id
        return name
    
    def _setupLocale(self):
        request = self.context.REQUEST
        # we already got it set up
        if hasattr(request, 'locale'):
            return
        # request doesn't have locale in Zope 2; this code should
        # ideally move somewhere into Five
        from zope.i18n.locales import locales, LoadLocaleError
        
        langs = IUserPreferredLanguages(request).getPreferredLanguages()
        for httplang in langs:
            parts = (httplang.split('-') + [None, None])[:3]
            try:
                request.locale = locales.getLocale(*parts)
                return
            except LoadLocaleError:
                # Just try the next combination
                pass
        else:
            # No combination gave us an existing locale, so use the default,
            # which is guaranteed to exist
            request.locale = locales.getLocale(None, None, None)
        
    def getLocale(self):
        # XXX zope 3 has locale on the request; Five doesn't have that yet
        langs = IUserPreferredLanguages(
            self.context.REQUEST).getPreferredLanguages()
        for httplang in langs:
            parts = (httplang.split('-') + [None, None])[:3]
            try:
                self._locale = locales.getLocale(*parts)
                return
            except LoadLocaleError:
                # Just try the next combination
                pass

            
        language = self.getPreferredLanguage()
        
        
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
