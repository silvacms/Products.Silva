# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

  First let's create a folder to play with our marker:

    >>> browser = SilvaBrowser()
    >>> logAsUser(app, 'manager')
    >>> app.root.manage_addProduct['Silva'].manage_addFolder('folder', 'Folder')
    ''
    >>> folder = app.root.folder

  Our purpose is to add a template called `photo`:

    >>> browser.go('http://localhost/root/folder/photo')
    (404, None)

  We can grokkify our marker:

    >>> grokkify('Products.Silva.tests.grok.markers')

  So now we should have it:

    >>> from silva.core.layout.interfaces import IMarkManager
    >>> from Products.Silva.tests.grok.markers import IPhotoFolderTag
    >>> manager = IMarkManager(folder)
    >>> manager.availablesMarkers
    [u'Products.Silva.tests.grok.markers.IPhotoFolderTag', 
     u'silva.core.layout.interfaces.ICustomizableMarker']
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> manager.addMarker(u'Products.Silva.tests.grok.markers.IPhotoFolderTag')

  And it will be available on the object:

    >>> manager = IMarkManager(folder)
    >>> manager.availablesMarkers
    [u'silva.core.layout.interfaces.ICustomizableMarker']
    >>> manager.usedMarkers
    ['Products.Silva.tests.grok.markers.IPhotoFolderTag']
    >>> IPhotoFolderTag.providedBy(folder)
    True
    >>> browser.go('http://localhost/root/folder/photo')
    (200, 'http://localhost/root/folder/photo')
    >>> browser.contents
    '<html><body>Photo !</body></html>'

  And we can remove it:

    >>> manager.removeMarker(u'Products.Silva.tests.grok.markers.IPhotoFolderTag')

  It won't exists anymore:
 
    >>> manager = IMarkManager(folder)
    >>> manager.availablesMarkers
    [u'Products.Silva.tests.grok.markers.IPhotoFolderTag', 
     u'silva.core.layout.interfaces.ICustomizableMarker']
    >>> manager.usedMarkers
    []
    >>> IPhotoFolderTag.providedBy(folder)
    False
    >>> browser.go('http://localhost/root/folder/photo')
    (404, None)


  And we remove our marker from the ZCA so others tests don't fail. 
  XXX We have to found something better than that:

    >>> from zope.component import getGlobalSiteManager
    >>> from silva.core.layout.interfaces import ICustomizableType
    >>> sm = getGlobalSiteManager()
    >>> sm.unregisterUtility(IPhotoFolderTag, ICustomizableType, 
    ...                      u'Products.Silva.tests.grok.markers.IPhotoFolderTag')
    True

"""

from silva.core.layout.interfaces import ICustomizableTag
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

class IPhotoFolderTag(ICustomizableTag):
    """Customization tag to get a folder as a photo folder.
    """


class Photo(silvaviews.Template):

    silvaconf.context(IPhotoFolderTag)

    def render(self):
        return u'<html><body>Photo !</body></html>'
