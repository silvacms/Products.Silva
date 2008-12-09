# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

from Products.Silva.i18n import translate as _
from smi import SMIButton


class EditButton(SMIButton):

    def available(self):
        return bool(self.context.get_unapproved_version())


class KupuEditorButton(EditButton):

    order = 10

    tab = 'tab_edit?editor=kupu'
    label = _(u"kupu editor")
    help = _(u"edit with the kupu editor: alt-(")
    accesskey = '('


class FormsEditorButton(EditButton):

    order = 20

    tab = 'tab_edit?editor=forms_editor'
    label = _(u"forms editor")
    help = _(u"edit with the forms editor: alt-)")
    accesskey = ')'

