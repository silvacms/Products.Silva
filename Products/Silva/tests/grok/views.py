# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

    >>> browser = get_browser()
    >>> browser.login('manager', 'manager')

 We grok this test file:

    >>> grok('Products.Silva.tests.grok.views')

 Now we add a folder:

    >>> root = get_root()
    >>> factory = root.manage_addProduct['Silva']
    >>> factory.manage_addMyFolder('myfolder', 'My Folder')
    >>> root.myfolder
    <MyFolder at /root/myfolder>
    >>> browser.open('http://localhost/root/myfolder')
    200
    >>> browser.content_type
    'text/html;charset=utf-8'
    >>> browser.html.xpath('//h1/text()')
    ['A customized Folder']


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
