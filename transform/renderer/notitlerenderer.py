# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase
from Products.SilvaDocument.Document import Document
from silva.core import conf as silvaconf

class NoTitleRenderer(XSLTRendererBase):

    silvaconf.title('Without Title Renderer (Same as basic but without the document title)')
    silvaconf.context(Document)
    silvaconf.XSLT('no_title.xslt')
