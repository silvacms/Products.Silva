import unittest
from urllib2 import HTTPError

from Products.Five.testbrowser import Browser

import SilvaTestCase

class MixinLoginLogout(object):
    """ Test login and logout in the Silva SMI for specific roles """
    
    def do_login(self, browser, url, username, password):
        """ Login to a url with username and password"""
        # make sure we can not use the edit page if we're not logged in
        try:
            browser.open(url)
        except HTTPError, err:
            self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
        else:
            self.fail()
        # now we'll try to login
        browser.addHeader('Authorization', 'Basic %s:%s' % (
                          username, password))
        browser.addHeader('Accept-Language', 'en-US')
        browser.open(url)
        self.assertEquals(url, browser.url)
    
    def do_logout(self, browser):
        # now, let's log out again..
        root_url = self.getRoot().absolute_url()
        logout_url = '%s/manage_zmi_logout' % root_url
        try:
            browser.open(logout_url)
        except HTTPError, err:
            self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
        else:
            self.fail()
        self.assertEquals('You have been logged out.' in browser.contents, True)
        return Browser()

class LoginTestCase(SilvaTestCase.SilvaFunctionalTestCase,
                    MixinLoginLogout):

    def test_manager_login(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        self.do_login(url, SilvaTestCase.user_name, SilvaTestCase.user_password)
        self.do_logout()

    def test_role_login(self):
        url = '%s/edit' % self.getRoot().absolute_url()
        for role in ['Reader', 'Author', 'Editor', 'ChiefEditor', 'Manager']:
            user = self.getRoot().acl_users._doAddUser('test%s' % role, 
                                                        'secret', 
                                                        [role],
                                                        [])
            self.do_login(url, 'test%s' % role, 'secret')
            self.do_logout()
            self.root.acl_users._doDelUsers(['test%s' % role])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LoginTestCase))
    return suite
