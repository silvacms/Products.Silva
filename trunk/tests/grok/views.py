# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

    >>> browser = SilvaBrowser()
    >>> logAsUser(app, 'manager')

 We grok this test file:

    >>> grokkify('Products.Silva.tests.grok.views')

 Now we add a folder:

    >>> app.root.manage_addProduct['Silva'].manage_addMyFolder('myfolder', 'My Folder')
    >>> app.root.myfolder
    <My Folder instance myfolder>
    >>> browser.go('http://localhost/root/myfolder')
    (200, 'http://localhost/root/myfolder')
    >>> print browser.contents
    <!DOCTYPE  ...
    <div>A customized Folder</div> ...


"""

from Products.Silva.Folder import Folder
from silva.core.views import views as silvaviews
from silva.core import conf as silvaconf

class MyFolder(Folder):

    meta_type = 'My Folder'

    silvaconf.factory('manage_addMyFolder')


def manage_addMyFolder(self, id, title, REQUEST=None):
    folder = MyFolder(id)
    self._setObject(id, folder)


class MyFolderView(silvaviews.View):

    silvaconf.context(MyFolder)



