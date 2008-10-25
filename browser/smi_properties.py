# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements

from Products.Silva.i18n import translate as _
from Products.Silva import interfaces
from Products.Silva.adapters.interfaces import ISubscribable

from Products.Silva.browser.interfaces import ISMIExecutorButton
from smi import SMIButton


class AddablesButton(SMIButton):

    order = 50

    tab = 'tab_addables'
    label = _(u"addables")
    help = _(u"change the addables allowed in this publication: alt-d")
    accesskey = 'd'


class SettingsButton(SMIButton):

    order = 10

    tab = 'tab_settings'
    label = _(u"settings")
    help = _(u"various settings: alt-e")
    accesskey = 'e'


class SubscriptionsButton(SMIButton):

    order = 110

    tab = 'tab_subscriptions'
    label = _(u"subscriptions")
    help = _(u"manage subscriptions: alt-u")
    accesskey = "u"

    def available(self):
        return ISubscribable(self.context, None) is not None


class PublishButton(SMIButton):

    implements(ISMIExecutorButton)

    order = 20

    label = _(u"publish now")
    help = _(u"publish this document: alt-p")
    accesskey = 'p'

    @property
    def tab(self):
        return 'quick_publish?return_to=%s' % self.view.tab_name

    def available(self):
        return bool(self.context.get_unapproved_version())
