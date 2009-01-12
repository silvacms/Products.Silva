# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class AuthorManagerScenarioOneTestCase(SilvaFunctionalTestCase):
    """
        login author
        select silva document
        make silva document
        enter silva document
        click preview
        logout
        login manager
        enter silva document
        click preview
        click publish
        click root
        delete
        logout
    """

    def test_author_manager_scenario_one(self):
        sb = SilvaBrowser()
        status, url = sb.login('author', 'secret', sb.smi_url())
        sb.make_content('Silva Document', id='test_document',
                         title='Test document')

        data = sb.get_content_data()
        self.assertEquals(data[1]['name'], u'Test document')
        sb.click_href_labeled('test_document')
        tab_name = sb.get_tabs_named('editor')
        self.failUnless(tab_name in sb.browser.contents)
        sb.click_tab_named('preview')
        self.assertEquals(sb.browser.url,
                          'http://nohost/root/test_document/edit/tab_preview')
        sb.logout()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        sb.click_href_labeled('test_document')
        tab_name = sb.get_tabs_named('editor')
        self.failUnless(tab_name in sb.browser.contents)
        sb.click_tab_named('preview')
        # get the url of the top frame, then click the button labeled publish now
        self.assertEquals(sb.browser.url,
                          'http://nohost/root/test_document/edit/tab_preview')
        preview_top_url = sb.get_frame_url(0)
        self.assertEquals(preview_top_url,
                          'http://nohost/root/test_document/edit/tab_preview_frame_top?message=&message_type=')
        sb.go(preview_top_url)
        status, url = sb.click_button_labeled('publish now')
        preview_top_url = sb.get_frame_url(0)
        self.assertEquals(preview_top_url,
                          'http://nohost/root/test_document/edit/tab_preview_frame_top?message=Version approved.&message_type=feedback')
        sb.go(preview_top_url)
        self.failUnless('Version approved.' in sb.browser.contents)
        sb.go(sb.smi_url())
        sb.select_delete_content('test_document')
        self.failUnless('test_document' in sb.get_content_ids())
        status, url = sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorManagerScenarioOneTestCase))
    return suite
