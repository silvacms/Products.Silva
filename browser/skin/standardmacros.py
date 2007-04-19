from Products.Five import BrowserView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.basicskin.standardmacros import StandardMacros as BaseMacros

class SilvaMacros(BrowserView):
    template = ViewPageTemplateFile('../../layout/layout_macro.html')

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        override_template = getattr(context, 'override.html', None)
        content_template = getattr(context, 'content.html', None)
        self.template = override_template or content_template or self.template

    def __getitem__(self, key):
        macro = self.template.macros[key]
        return macro

class SilvaBareMacros(BrowserView):
    template = ViewPageTemplateFile('bare.pt')

    def __getitem__(self, key):
        return self.template.macros[key]


class StandardMacros(BaseMacros):
    macro_pages = ('silva_macros',)

class StandardBareMacros(BaseMacros):
    macro_pages = ('silva_bare_macros',)
