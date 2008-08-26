# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

    >>> from Products.Silva.ExtensionRegistry import extensionRegistry 
    >>> silva = extensionRegistry.get_extension('Silva')
    >>> root = getSilvaRoot()
    >>> browser = getSilvaBrowser()

  You can grok your contents. Since our test are in Silva, they will
  be registered for Silva here.


  On a publication:

    >>> grokkify('Products.Silva.tests.grok.contents_publication_fixture')
    >>> 'My Publication' in [content['name'] for content in silva.get_content()]
    True

  We will be able to add that special publication:

    >>> browser.login(url=browser.smi_url())
    >>> browser.get_addables_list()

  A version content should have a versionClass defined:

    >>> grokkify('Products.Silva.tests.grok.contents_noversionclass_fixture')
    Traceback (most recent call last):
       ...
    GrokError: You need to provide a version class for MyVersionedContent.


"""

