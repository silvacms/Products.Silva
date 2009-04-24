# this is a package

from five import grok

class SilvaGlobals(grok.DirectoryResource):
    # This export the globals directory using Zope 3 technology.
    grok.path('scripts')
    grok.name('Products.Silva.browser.scripts')
