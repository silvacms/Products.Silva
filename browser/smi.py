# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from zope.i18n import translate
from zope.cachedescriptors.property import CachedProperty

from Products.Five import BrowserView
from Products.Five.viewlet.manager import ViewletManagerBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import interfaces

class SMITab(BrowserView):
    """A SMI tab.
    """

    template = ViewPageTemplateFile('templates/tabsmi.pt')

    implements(interfaces.ISMITab)

    def __call__(self):
        return self.template()


class EditTab(SMITab):
    """Edit
    """

    implements(interfaces.IEditTab)

    tab_name = 'tab_edit'


class AccessTab(SMITab):
    """Access
    """

    implements(interfaces.IAccessTab)

    tab_name = 'tab_access'


class PropertiesTab(SMITab):
    """Properties
    """

    implements(interfaces.IPropertiesTab)

    tab_name = 'tab_metadata'


class PreviewTab(SMITab):
    """Preview
    """

    implements(interfaces.IPreviewTab)

    tab_name = 'tab_preview'



class SMIButtonViewletManager(ViewletManagerBase):

    def sort(self, viewlets):
        return sorted(viewlets, lambda a, b: cmp(a[1].order, b[1].order))

    @CachedProperty
    def buttons(self):
        return (viewlet for viewlet in self.viewlets if \
                    not interfaces.ISMISpecialButton.providedBy(viewlet))

    @CachedProperty
    def executors(self):
        return (viewlet for viewlet in self.viewlets if \
                    interfaces.ISMIExecutorButton.providedBy(viewlet))

from Acquisition import Explicit

class ViewletBase(Explicit):
    """A Grok compatible viewlet base.
    """

    implements(interfaces.IViewlet)

    order = 0

    def __init__(self, context, request, view, manager):
        self.context = context
        self.request = request
        self.__parent__ = view
        self.view = view
        self.manager = manager
        self.viewletmanager = manager

    def update(self):
        pass

    def render(self):
        return u''


class SMIButton(ViewletBase):


    implements(interfaces.ISMIButton)
    template = ViewPageTemplateFile('templates/smibutton.pt')

    label = None
    tab = None
    help = None
    accesskey = None

    def formatedLabel(self):
        if interfaces.ISMISpecialButton.providedBy(self):
            return self.label
        return translate(self.label, context=self.request) + '...'

    def available(self):
        return True

    @property
    def selected(self):
        return self.request.URL.endswith(self.tab)

    def render(self):
        if self.available():
            return self.template()
        return u''
