# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest
from SilvaBrowser import SilvaBrowser
from SilvaTestCase import SilvaFunctionalTestCase

class QuotaTestCase(SilvaFunctionalTestCase):
    """
       [x]login manager
       [x]enable quota
       [x]put on file
       [x]check parameters/settings screen
       [x]set a quota
       [x]check changes
       [x]go back on contents
       [x]add a folder
         [x]add a publication
           [x]add a folder
             [x]add a file
             [x]add a publication
       [x]go on parameters/settings screen
       [x]check acquired quota
       [x]put a correct quota
       [x]check screen
       [x]put 0/empty quota
       [x]check screen
       [x]put an invalid quota
       [x]check screen (should get an error)
    """

    # default message reported by the interface.
    quota_report = 'The quota for this area is set to %d MB.'
    quota_error = "The quota can't be negative or bigger than the quota of the parent container."

    def container_tree(self):
	"""
            content = {
	        first: {
                    'type': 'Silva Folder',
                    'id': 'folder1',
                    'title': 'folder 1',
                    'policy': 'Silva Document',
                },
            }

            for item in content:
                make_content()
                self.failUnless(new content isn't in browser)
                click_href_labeled(new content)

	    make_content(folder1)
	    test content
	    click_href_labeled(folder1)
	    test inside content
            make_content(folder2)
	"""

    def util_goOnSettings(self):
        """Go on the settings tab of an item.
        """
        # go on properties tab
        self.sb.click_href_labeled('properties')
        self.failUnless(self.sb.get_listing_h2().startswith('properties of'))
        # access to the settings tab
        self.sb.click_href_labeled('settings...')
        self.failUnless(self.sb.get_listing_h2().startswith('settings for'))

    def set_quota(self, quota, expected_quota=None, expect_error=False):
        """Set the quota value, and expect a reply or an error.
        """
        self.sb.browser.getControl(name='silva-quota.quota:record').value = quota
        # There is several save metadata button, but they should all do the same.
        self.sb.browser.getControl(name='save_metadata:method', index=0).click()
        if not (expected_quota is None):
            msg = self.quota_report % expected_quota
            self.failUnless(msg in self.sb.browser.contents, 'No message "%s" in browser.' % msg)
        if expect_error:
            self.failUnless(self.quota_error in self.sb.browser.contents)
        else:
            self.failIf(self.quota_error in self.sb.browser.contents)

    def build_browser(self):
        """Create a SilvaBrowser.
        """
        # initializes silva browser
        self.sb = SilvaBrowser()
        status, url = self.sb.login('manager', 'secret', self.sb.smi_url())
        self.assertEqual(status, 200)
        url = self.sb.get_root_url()
        url = url + '/manage_main'
        self.sb.go(url)

    def enable_quota(self):
        """Go in ZMI, and on service_extension enable the quota system.
        """

        self.failUnless('Silva /edit...' in self.sb.browser.contents)
        self.sb.click_href_labeled('Services')
        self.assertEquals(
            self.sb.get_url(),
            'http://nohost/root/manage_services')
        self.sb.click_href_labeled('Services')
        self.assertEquals(
            self.sb.get_url(),
            'http://nohost/root/manage_services')
        self.sb.click_href_labeled(
            'service_extensions (Silva Product and Extension Configuration)')
        self.failUnless('Silva Services' in self.sb.browser.contents)
        self.sb.click_button_labeled('enable quota subsystem')
        self.failUnless('Quota sub-system enabled' in self.sb.browser.contents)
        self.sb.click_href_labeled('root')
        self.failUnless('Silva Root\n' in self.sb.browser.contents)
        self.sb.click_href_labeled('Silva /edit...')
        self.assertEquals(self.sb.get_url(), 'http://nohost/root/edit')


    """
    def test_overquota(self):
        #Test that when you add/edit a file and you are
        #overquota you get the corresponding error.
        #

        self.build_browser()
        self.enable_quota()

        # go on settings and check the acquired quota
        self.util_goOnSettings()


        # check and set quota
	byte_span = '<span title=" 0 Bytes">'
        self.failUnless(byte_span in self.sb.browser.contents)
        self.set_quota('10', 'quota for this area set to 10 MB')
        self.sb.click_href_labeled('contents')

        # create a folder and a publication

        # create a folder, called folder1
        self.sb.make_content('Silva Folder', id='folder1', title='Folder 1',
                                        policy='Silva Document')
        self.failUnless(self.sb.get_status_feedback().startswith('Added Silva Folder'))
        self.sb.click_href_labeled('folder1')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva Folder'))

        #create a publication inside of folder1, called publication1
        self.sb.make_content('Silva Publication', id='publication1', title='Publication 1',
                                        policy='Silva Document')
        self.failUnless(self.sb.get_status_feedback().startswith('Added Silva Publication'))
        self.sb.click_href_labeled('publication1')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva Publication'))

        # go on settings and check the acquired quota
        self.util_goOnSettings()

        # check acquired quota
        self.failUnless('quota for this area set to 10 MB' in self.sb.browser.contents)

        #set the quota for the publication
        self.set_quota('1', 'quota for this area set to 1 MB')
        self.sb.click_href_labeled('contents')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva Publication'))

        # upload a small file
        self.sb.make_content('Silva Image', image='torvald.jpg',
                                            id='file1', title='File 1')
        self.failUnless(self.sb.get_status_feedback().startswith('Added Silva Image'))

        # upload a 2nd bigger file
        self.sb.browser.handleErrors = False
        self.sb.make_content('Silva File', id='file2', title='File 2',
                                      file='beameruserguide.pdf')
        self.failUnless(self.sb.get_alert_feedback().startswith('You are overquota'))



        #logout
        status, url = self.sb.click_href_labeled('logout')
        self.assertEquals(status, 401)
    """

    def test_setquota(self):
        """Test modification of the quota's value.
        """

        self.build_browser()
        self.enable_quota()

        self.util_goOnSettings()

        # check and set quota
	byte_span = '<span title=" 0 Bytes">'
        self.failUnless(byte_span in self.sb.browser.contents)
        self.set_quota('10', expected_quota=10)
        self.sb.click_href_labeled('contents')

        self.sb.make_content('Silva File', id='quota_test', title='q test',
                             file='docs_export_2008-06-11.odt')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva File'))


        # try to get the size of the added file in order to see if
        # it's really here check changes

        self.sb.click_href_labeled('test')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva File'))
        self.sb.click_href_labeled('properties')
        self.failUnless(self.sb.get_listing_h2().startswith('properties of'))

        self.sb.click_href_labeled('settings...')
        byte_span = '<span title=" 1444981 Bytes">'
        self.failUnless(byte_span in self.sb.browser.contents)


        # this allows me to come back to the Silva root page
        # go back on contents = 3 times go back browser button

        self.sb.go_back()
        self.sb.go_back()
        self.sb.go_back()

        self.failUnless(self.sb.get_listing_h2().startswith('Silva Root'))

        # create a folder, called folder1
        self.sb.make_content('Silva Folder', id='folder1', title='Folder 1',
                             policy='Silva Document')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva Folder'))
        self.sb.click_href_labeled('folder1')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva Folder'))

        # create a publication inside of folder1, called publication1
        self.sb.make_content(
            'Silva Publication', id='publication1', title='Publication 1',
            policy='Silva Document')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva Publication'))
        self.sb.click_href_labeled('publication1')
        self.failUnless(
            self.sb.get_listing_h2().startswith('Silva Publication'))

        # create a folder inside of publication1, called folder2
        self.sb.make_content('Silva Folder', id='folder2', title='Folder 2',
                             policy='Silva Document')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva Folder'))
        self.sb.click_href_labeled('folder2')
        self.failUnless(self.sb.get_listing_h2().startswith('Silva Folder'))

        # add a publication
        self.sb.make_content(
            'Silva Publication', id='publication2', title='Publication 2',
                             policy='Silva Document')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva Publication'))

        # add a file
        self.sb.make_content('Silva File', id='file1', title='File 1',
                             file='docs_export_2008-06-11.odt')
        self.failUnless(
            self.sb.get_status_feedback().startswith('Added Silva File'))

        # go back to publication 1
        self.sb.browser.getLink('Publication 1').click()

        # go on settings and check the acquired quota
        self.util_goOnSettings()

        # check acquired quota
        self.failUnless((self.quota_report % 10) in self.sb.browser.contents)

        # put a correct quota
        self.set_quota('5', expected_quota=5)

        # put a quota == 0
        self.set_quota('0', expected_quota=10)
        self.set_quota('', expected_quota=10)

        # put a quota which is too big
        self.set_quota('100', expect_error=True)
        # reset error
        self.set_quota('', expected_quota=10)

        # put a quota which is negative
        self.set_quota('-3', expect_error=True)
        # reset error
        self.set_quota('', expected_quota=10)

        #logout
        status, url = self.sb.click_href_labeled('logout')
        self.assertEquals(status, 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuotaTestCase))
    return suite






