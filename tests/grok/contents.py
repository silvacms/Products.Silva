# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
"""

  You can grok your contents.


  On a publication:

    >>> grokkify('Products.Silva.tests.grok.contents_publication_fixture')

  A version content should have a versionClass defined:

    >>> grokkify('Products.Silva.tests.grok.contents_noversionclass_fixture')
    Traceback (most recent call last):
       ...
    GrokError: You need to provide a version class for MyVersionedContent.


"""

