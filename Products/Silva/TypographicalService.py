# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Silva
from Products.Silva import SilvaPermissions
from Products.Silva.helpers import add_and_edit

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf

_default_typo_chars = ['&#x20AC;',
                       '&#x201A;',
                       '&#x91;',
                       '&#x92;',
                       '&#x84;',
                       '&#x93;',
                       '&#x94;',
                       '&#xAB;',
                       '&#xBB;',
                       '&#x2014;',
                       '&#x2013;',
                       '&#xB7;',
                       '&#xA9;']


class TypographicalService(SilvaService):
    """This service stores non-keyboard characters"""

    security = ClassSecurityInfo()
    meta_type = 'Silva Typographical Characters Service'

    manage_options = (
        {'label':'Edit',
         'action':'manage_main'},
        ) + SilvaService.manage_options
    manage_main = manage_edit = PageTemplateFile(
        'www/typoService_edit', globals(),
        __name__='manage_main')

    silvaconf.icon('www/typochars_service.png')
    silvaconf.factory('manage_addTypographicalServiceForm')
    silvaconf.factory('manage_addTypographicalService')

    def __init__(self,id,title):
        self.id = id
        self.title = title
        self._typo_chars = _default_typo_chars

    #return a copy o the typo chars list
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'getTypoChars')
    def getTypoChars(self):
        return self._typo_chars[:]

    #add a list of typo chars
    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'setTypoChars')
    def setTypoChars(self, chars):
        self._typo_chars = []
        for c in chars:
            if c not in self._typo_chars:
                self._typo_chars.append(c)

    security.declareProtected(SilvaPermissions.ViewManagementScreens,
                              'edit_typoService')
    def edit_typoService(self, REQUEST):
        '''Save the typo characters'''
        #get chars from request
        chars = REQUEST.get('chars',_default_typo_chars)
        if not isinstance(chars,type([])):
            chars = chars.replace('\r','')
            chars = chars.replace('\n','')
            chars = chars.split(' ')
        self.setTypoChars(chars)
        return self.manage_main(manage_tabs_message='Saved Characters')
InitializeClass(TypographicalService)

manage_addTypographicalServiceForm = PageTemplateFile("www/typoServiceAdd", globals(),
                                            __name__='manage_addTypographicalServiceForm')

def manage_addTypographicalService(self, id, REQUEST=None):
    """Add a typo service"""
    obj = TypographicalService(id,'Typographical Characters Service')
    self._setObject(id, obj)
    obj = getattr(self, id)
    add_and_edit(self, id, REQUEST)

