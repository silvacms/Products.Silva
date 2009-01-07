# Copyright (c) 2003-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: Document.py,v 1.86 2006/01/24 16:14:12 faassen Exp $

# The sole purpose of this module is to allow Silva Documents from 0.9.2 to 
# be unpickled so the upgrading mechanismn can read and transform them into
# 0.9.3 Documents.

import zLOG
zLOG.LOG('Silva', zLOG.WARNING, 'Silva Documents require upgrading.',
    'There are Silva Documents which have not been upgraded to Silva 0.9.3.\n'
    'Upgrade via service_extensions.\n')

from Products.SilvaDocument.Document import Document, DocumentVersion

