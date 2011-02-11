# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.component import getUtility
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.http import HTTPCharsets as ZopeHTTPCharsets
from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages
from zope.publisher.browser import BrowserLanguages
from zope.i18n.locales import locales, LoadLocaleError

from DateTime import DateTime

from five import grok
from silva.core.views.interfaces import IVirtualSite
from silva.core.interfaces.adapters import ILanguageProvider


def canonalize_language(code):
    # make sure that language ids like zh_TW are translated into
    # browser-format, namely zh-tw
    if '_' in code:
        language_id, language_variant = code.split('_')
        return '%s-%s' % (language_id, language_variant.lower())
    return code


class HTTPCharsets(ZopeHTTPCharsets, grok.Adapter):
    grok.context(IBrowserRequest)

    def getPreferredCharsets(self):
        # Fix HTTPCharsets like done in zope.publisher 3.12.5, to
        # prevent UnicodeDecodeError in page templates.
        charsets = ZopeHTTPCharsets.getPreferredCharsets(self)
        if charsets == []:
            charsets = ['utf-8']
        return charsets


class LanguageProvider(grok.Adapter):
    """Information about available languages.
    """
    grok.context(IBrowserRequest)
    grok.implements(ILanguageProvider)
    grok.provides(ILanguageProvider)

    def __init__(self, request):
        self.request = request
        self.__setupLocale()

    def __setupLocale(self):
        if hasattr(self.request, 'locale'):
            return
        # request doesn't have locale in Zope 2; this code should
        # ideally move somewhere into Five

        langs = IUserPreferredLanguages(self.request).getPreferredLanguages()
        for httplang in langs:
            parts = (httplang.split('-') + [None, None])[:3]
            try:
                self.request.locale = locales.getLocale(*parts)
                return
            except LoadLocaleError:
                # Just try the next combination
                pass
        else:
            # No combination gave us an existing locale, so use the default,
            # which is guaranteed to exist
            self.request.locale = locales.getLocale(None, None, None)

    def getAvailableLanguages(self):
        domain = getUtility(ITranslationDomain, 'silva')
        return map(canonalize_language, domain._catalogs.keys())

    def getLanguageName(self, language_id):
        """Get the name of the language, in the current language.
        """
        # deal with languages that are not in the language types listing
        # in Zope 3. Namely everything with a dash in the middle.
        # It's possible that in later Zope 3 versions the database is
        # more extensive and does provide language names for these
        # languages - the maintainer reading this code could check.
        if '-' in language_id:
            language_id, language_variant = language_id.split('-')
        else:
            language_variant = None
        name = self.request.locale.displayNames.languages.get(language_id)
        if name is None:
            # if for some reason the language name is unknown, show id
            name = language_id
        if language_variant is not None:
            name = name + ' (%s)' % language_variant
        return name

    def setPreferredLanguage(self, language):
        response = self.request.response
        path = IVirtualSite(self.request).get_root().absolute_url_path()
        if not language:
            response.expireCookie('silva_language', path=path)
            return
        response.setCookie(
            'silva_language', language,
            path=path, expires=(DateTime()+365).rfc822())

    def getPreferredLanguage(self):
        langs = IUserPreferredLanguages(self.request).getPreferredLanguages()
        if not langs:
            return None
        return canonalize_language(langs[0])


# new language extractor that looks in the silva_language cookie first,
# then fall back on browser setting

class SilvaLanguages(BrowserLanguages):

    def getPreferredLanguages(self):
        languages = super(SilvaLanguages, self).getPreferredLanguages()
        cookie_language = self.request.cookies.get('silva_language')
        if cookie_language is not None:
            languages = [cookie_language] + languages
        return languages
