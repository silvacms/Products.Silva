# -*- coding: utf-8 -*-
# Copyright (c) 2008-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

    >>> from Products.Silva.ExtensionRegistry import extensionRegistry
    >>> silva = extensionRegistry.get_extension('Silva')

  You can grok your contents. Since our test are in Silva, they will
  be registered for Silva here.

  On a publication:

    >>> grok('Products.Silva.tests.grok.contents_publication_fixture')
    >>> 'My Publication' in [content['name'] for content in silva.get_content()]
    True

  To be able to create this publication we need to install it
  first. But we have no installer.

  For a versioned content we have an example in that file. We define
  here a custom factory, which just create a article, so we will be
  able to create an instance:

    >>> grok('Products.Silva.tests.grok.contents')
    >>> 'My Article' in [content['name'] for content in silva.get_content()]
    True
    >>> 'My Article Version' in [content['name'] for content in silva.get_content()]
    True
    >>> root = get_root()
    >>> factory = root.manage_addProduct['Silva']
    >>> factory.manage_addMyArticle('myarticle', 'My demo article')
    >>> root.myarticle
    <Article at /root/myarticle>
    >>> root.myarticle.customCreation
    True

  A versioned content should have a versionClass defined:

    >>> grok('Products.Silva.tests.grok.contents_noversionclass_fixture')
    Traceback (most recent call last):
       ...
    GrokError: You need to provide a version class for MyVersionedContent.


"""

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version
from Products.Silva.helpers import add_and_edit

from silva.core import conf as silvaconf

class ArticleVersion(Version):
    meta_type = 'My Article Version'


class Article(VersionedContent):
    meta_type = 'My Article'

    silvaconf.versionClass(ArticleVersion)
    silvaconf.factory('manage_addMyArticle')

    customCreation = False      # For test only


def manage_addMyArticle(self, id, title, REQUEST=None):
    """Custom factory to show off that you can provide your own
    factory.
    """

    article = Article(id)
    self._setObject(id, article)
    article = getattr(self, id)
    # For test only
    article.customCreation = True
    # As well we should create a version, and other stuff ...
    add_and_edit(self, id, REQUEST)
