# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from zope.component import getUtility
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.i18n.interfaces import ITranslationDomain, IUserPreferredLanguages

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


class LanguageProvider(grok.Adapter):
    """Information about available languages.
    """
    grok.context(IBrowserRequest)
    grok.implements(ILanguageProvider)
    grok.provides(ILanguageProvider)

    def __init__(self, request):
        self.request = request

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
        path = IVirtualSite(self.request).get_root_path()
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


