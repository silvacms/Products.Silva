# -*- coding: utf-8 -*-
# Copyright (c) 2008-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from SilvaTestCase import SilvaFunctionalTestCase
from SilvaBrowser import SilvaBrowser, Z3CFORM_FORM

class SilvaBrowserTest(SilvaFunctionalTestCase):
    """
        test the basic SilvaBrowser API methods
    """
    def test_silvabrowser(self):
        sb = SilvaBrowser()

    def test_login_logout(self):
        # login
        sb = SilvaBrowser()
        # goto silva root
        status, url = sb.go(self.silva_url)
        self.assertEquals(status, 200)
        # goto edit page
        status, url = sb.go(sb.smi_url())
        self.assertEquals(status, 401)
        # besides the 401, url will be None,
        # since we didn't go anywhere
        self.assertEquals(url, None)
        # login fake user
        status, url = sb.login('skdgsdkj', 'zxcmnbvx', sb.smi_url())
        self.assertEquals(status, 401)
        # login manager
        status, url = sb.login('manager', 'secret', sb.smi_url())
        self.assertEquals(status, 200)
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

    def test_delete_published_content(self):
        # login
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # get silva content
        data = sb.get_content_data()
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['name'], u'Welcome to Silva!')
        content_id = data[0]['id']
        sb.select_content(content_id)
        status, url = sb.click_button_labeled('delete')
        # test alert msg
        self.failUnless(sb.get_alert_feedback().startswith('Could not delete'))
        sb.select_content(content_id)
        status, url = sb.click_button_labeled('close')
        # test status msg
        self.failUnless(sb.get_status_feedback().startswith('Closed'))
        # delete content
        sb.select_content(content_id)
        status, url = sb.click_button_labeled('delete')
        self.failUnless(sb.get_status_feedback().startswith('Deleted'))
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

    def test_get_all_content(self):
        # login
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # make some content
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Document' in addables)
        sb.select_addable('Silva Document')
        # create silva document
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title() == 'create Silva Document')
        # fill in form fields
        sb.form_type = Z3CFORM_FORM
        sb.set_id_field('test_content')
        sb.set_title_field('test content')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Document' in addables)
        sb.select_addable('Silva Document')
        # create silva document
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title() == 'create Silva Document')
        # fill in form fields
        sb.set_id_field('test_content2')
        sb.set_title_field('test content2')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
        # get all silva content
        data = sb.get_content_data()
        sb.select_all_content(data)
        # close published content
        status, url = sb.click_button_labeled('close')
        self.failUnless(sb.get_status_feedback().startswith('Closed'))
        data = sb.get_content_data()
        sb.select_all_content(data)
        # delete content
        status, url = sb.click_button_labeled('delete')
        self.failUnless(sb.get_status_feedback().startswith('Deleted'))
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

    # test field filling methods
    def test_make_silva_document(self):
        # login
        sb = SilvaBrowser()
        status, url = sb.login('manager', 'secret', sb.smi_url())
        # select meta_type
        addables = sb.get_addables_list()
        self.failUnless('Silva Document' in addables)
        sb.select_addable('Silva Document')
        # create silva document
        status, url = sb.click_button_labeled('new...')
        self.failUnless(sb.get_addform_title() == 'create Silva Document')
        # fill in form fields
        sb.form_type = Z3CFORM_FORM
        sb.set_id_field('test_content')
        sb.set_title_field('test content')
        status, url = sb.click_button_labeled('save')
        self.failUnless(sb.get_status_feedback().startswith('Added Silva Document'))
        # delete content
        data = sb.get_content_data()
        # get the right content
        self.assertEquals(data[1]['name'], u'test content')
        sb.select_content('test_content')
        status, url = sb.click_button_labeled('delete')
        self.failIf('test content' in sb.get_content_ids())
        # logout
        status, url = sb.click_href_labeled('logout Manager manager')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaBrowserTest))
    return suite
