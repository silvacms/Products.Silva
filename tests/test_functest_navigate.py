# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from FunctionalTestMixin import *
import SilvaTestCase

class NavigateTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                       MixinRoleContent, MixinNavigate):
    """
        test navigation tabs as manager at Silva root
    """
    def url(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        return url
    
    def test_content_tab(self):
        url = self.url()
        self.do_navigate(SilvaTestCase.user_manager, success, contents, url)
    
    def test_preview_tab(self):
        url = self.url()
        self.do_navigate(SilvaTestCase.user_manager, success, preview, url)

    def test_properties_tab(self):
        url = self.url()
        self.do_navigate(SilvaTestCase.user_manager, success, properties, url)
        
    def test_access_tab(self):
        url = self.url()
        self.do_navigate(SilvaTestCase.user_manager, success, access, url)
        
    def test_publish_tab(self):
        url = self.url()
        self.do_navigate(SilvaTestCase.user_manager, success, publish, url)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NavigateTestCase))
    return suite
