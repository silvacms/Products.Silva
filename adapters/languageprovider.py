# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.component import getUtility
from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages
from zope.interface import implements
from zope.publisher.browser import BrowserLanguages

from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime

from Products.Silva.adapters import adapter
from Products.Silva import SilvaPermissions

from silva.core.interfaces.adapters import ILanguageProvider
from silva.translations import translate as _


# XXX this isn't a real z3 adapter yet as it's used by view code
class LanguageProvider(adapter.Adapter):
    """
    """
    implements(ILanguageProvider)

    security = ClassSecurityInfo()
    security.declareObjectProtected(SilvaPermissions.ReadSilvaContent)

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        silva_domain = getUtility(ITranslationDomain, 'silva')
        # XXX awful hack, but we don't have access to any
        # 'getAvailableLanguages' functionality apparently..
        result = ['none']
        for key in silva_domain._catalogs.keys():
            # make sure that language ids like zh_TW are translated into
            # browser-format, namely zh-tw
            if '_' in key:
                language_id, language_variant = key.split('_')
                result.append('%s-%s' % (language_id,
                                         language_variant.lower()))
            else:
                result.append(key)
        return result

    security.declarePublic('getLanguageName')
    def getLanguageName(self, language_id):
        """Get the name of the language, in the current language.
        """
        if language_id == 'none':
            return _(u'Use browser language setting')
        self._setupLocale()
        # deal with languages that are not in the language types listing
        # in Zope 3. Namely everything with a dash in the middle.
        # It's possible that in later Zope 3 versions the database is
        # more extensive and does provide language names for these
        # languages - the maintainer reading this code could check.
        if '-' in language_id:
            language_id, language_variant = language_id.split('-')
        else:
            language_variant = None
        name = self.context.REQUEST.locale.displayNames.languages.get(
            language_id)
        if name is None:
            # if for some reason the language name is unknown, show id
            name = language_id
        if language_variant is not None:
            name = name + ' (%s)' % language_variant
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

    security.declarePublic('setPreferredLanguage')
    def setPreferredLanguage(self, language):
        response = self.context.REQUEST.RESPONSE
        path = '/'.join(
            self.context.get_publication().get_root().getPhysicalPath())
        if language == 'none':
            response.expireCookie('silva_language', path=path)
            return
        response.setCookie(
            'silva_language', language,
            path=path, expires=(DateTime()+365).rfc822())

    security.declarePublic('getPreferredLanguage')
    def getPreferredLanguage(self):
        try:
            return IUserPreferredLanguages(
                self.context.REQUEST).getPreferredLanguages()[0]
        except IndexError:
            return None


InitializeClass(LanguageProvider)


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
