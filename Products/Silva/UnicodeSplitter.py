# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import zope.deferredimport

zope.deferredimport.deprecated(
    'Please run zodbupdate.',
    Splitter='silva.core.services.splitter:Splitter')

