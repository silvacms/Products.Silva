# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Silva
from Products.Silva.transform.renderer.xsltrendererbase import XSLTRendererBase
from Products.SilvaDocument.Document import Document
from silva.core import conf as silvaconf

class ImagesOnRightRenderer(XSLTRendererBase):
    
    silvaconf.title('Images on Right')
    silvaconf.context(Document)
    silvaconf.XSLT('images_to_the_right.xslt')

