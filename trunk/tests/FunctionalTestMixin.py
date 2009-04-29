# -*- coding: utf-8 -*-
# Copyright (c) 2008-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
from urllib2 import HTTPError
import re, os.path

# Zope
from Products.Five.testbrowser import Browser

# Silva
from helpers import openTestFile
import SilvaTestCase

# Expected state of creation
fail_login = object()
fail_nothing_addable = object()
fail_not_addable = object()
success = object()

# Expected tab properties
contents = []
preview = []
properties = []
access = []
publish = []

contents.append('contents')
contents.append('add a new item')
preview.append('preview')
preview.append('root &#8211;\n   preview')
properties.append('properties')
properties.append('various settings:')
access.append('access')
access.append('restrict access to users with a specific role')
publish.append('publish')
publish.append('publishing actions')


class BaseMixin(object):
     def setUpMixin(self):
        """Set up method for test mixin class
        """
        pass


class MixinLoginLogout(BaseMixin):
    """ Test login and  logout in the Silva SMI for specific roles """

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


class MixinFieldParameters(BaseMixin):

    def fill_create_file_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_file_field(browser)

    def fill_create_image_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_image_field(browser)

    def fill_create_link_fields(self, browser):
        self.fill_create_title_field(browser)
        self.fill_create_url_field(browser)
        self.fill_create_link_type_field(browser)

    def fill_create_depth_field(self, browser):
        self.fill_create_title_field(browser)
        browser.getControl(name='field_depth').value = '-1'

    def fill_create_file_field(self, browser):
        browser.getControl(name='field_file').add_file(openTestFile('test.txt'), 'text/plain', 'test.txt')

    def fill_create_folderish_field(self, browser):
        self.fill_create_title_field(browser)
        browser.getControl(name='field_policy_name').value = ['Silva Document']

    def fill_create_ghost_url_field(self, browser):
        browser.getControl(name='field_content_url').value = 'index'

    def fill_create_image_field(self, browser):
        browser.getControl(name='field_file').add_file(openTestFile('torvald.jpg'), 'image/jpeg', 'torvald.jpg')

    def fill_create_link_type_field(self, browser):
        browser.getControl(name='field_link_type').value = ['absolute']

    def fill_create_properties_title_field(self, browser):
        browser.getControl(name='silva-content.maintitle:record').value = 'test content€'

    def fill_create_title_field(self, browser):
        browser.getControl(name='field_object_title').value = 'test content€'
        # other unicode characters to choose from '€ ‚ ‘ ’ „ “ ” « » — – · ©'

    #def fill_create_title_field2(self, browser):
    #    browser.getControl(name='field_object_title').value = 'test content2'

    def fill_create_url_field(self, browser):
        browser.getControl(name='field_url').value = 'index'

class MixinRoleContent(MixinLoginLogout):

    def role_logout(self, browser):
        self.do_logout(browser)

    def role_login_edit(self, browser, user_name, result, base=None):
        role = SilvaTestCase.users[user_name]['role']
        password = SilvaTestCase.users[user_name]['password']
        if base is None:
            url = '%s/edit' % self.getRoot().absolute_url()
        else:
            url = '%s/%s/edit' % (self.getRoot().absolute_url(), base)
        # Try login
        try:
            self.do_login(browser, url, user_name, password)
        except HTTPError, err:
            if result is fail_login:
                self.assertEquals(str(err), 'HTTP Error 401: Unauthorized')
            else:
                self.fail()
        # Check the role
        p = re.compile('logout\s+%s' % role)
        p.findall(browser.contents)
        self.failUnless(p, "The role '%s' does not match logout message" % role)

    def do_create_content(self, browser, content_type, creator, result, item_id='test_content'):
        # Test if role has access to no content_types
        try:
            meta_type = browser.getControl(name="meta_type")
        except LookupError:
            if result is fail_nothing_addable:
                return
            self.fail()
        # Test if role has access to content_type
        if result is fail_not_addable:
            self.failIf(content_type in meta_type.options,
                        "Role has access to this '%s'" % meta_type)
        else:
            self.failUnless(content_type in meta_type.options,
                            "Content type '%s' is not included as meta_type"
                            % content_type)
            # Create the content
            browser.getControl(name='meta_type').value = [content_type]
            browser.getControl(name='add_object:method').click()
            browser.getControl(name='field_object_id').value = item_id
            if creator:
               creator(browser)
            browser.getControl(name='add_submit').click()
            self.failUnless('Added %s' % content_type in browser.contents,
                            "Content type: '%s' is not included in submit "
                            "feedback message" % content_type)
            self.failUnless(item_id in browser.contents)

    def do_delete_content(self, browser, id="test_content"):
        # Delete the content
        browser.getControl(name='ids:list').value = [id]
        browser.getControl(name='tab_edit_delete:method').click()
        self.failUnless('Deleted' in browser.contents)

    def do_make_content(self, user_name, content_type, creator, result, base=None, delete=True):
        """
            this method takes a role, logs the user (role) in, selects a content
            type, makes the content type, then deletes the content type, and
            then logs the user out
        """
        browser = Browser()
        self.role_login_edit(browser, user_name, result, base=base)
        if result is fail_login:
            return
        self.do_create_content(browser, content_type, creator, result)
        if result is success and delete:
            self.do_delete_content(browser)
        self.role_logout(browser)

    def do_login_and_delete_content(self, user_name, result, base=None):
        browser = Browser()
        self.role_login_edit(browser, user_name, result, base=base)
        if result is fail_login:
            return
        self.do_delete_content(browser)
        self.role_logout(browser)

class MixinNavigate(MixinLoginLogout):
    """
        methods that simulate or support navigating the smi
    """

    def setUpMixin(self):
        super(MixinNavigate, self).setUpMixin()
        self.root_url = '%s/edit' % self.getRoot().absolute_url()
        self.content_url = '%s/edit/tab_edit' % self.getRoot().absolute_url()
        self.content_type_url = '%s/content_test/edit/tab_edit' % self.getRoot().absolute_url()

    def do_navigate(self, user_name, result, tab_properties, url, base=None):
        """
            this method is used with navigate_tab to test all the navigation
            tabs
        """
        browser = Browser()
        self.role_login_edit(browser, user_name, result, base=base)
        if result is fail_login:
            return
        self.navigate_tab(browser, tab_properties, url)
        self.role_logout(browser)

    def navigate_tab(self, browser, tab_properties, url):
        """
            this method tests all the Silva tabs
        """

        browser.open(url)
        link = browser.getLink(tab_properties[0])
        link.click()
        self.failUnless(tab_properties[1] in browser.contents,
                        "title attribute '%s' is not included in browser "
                         "content" % tab_properties[1])

    def zmi_link_builder(self):
        return

    def tab_link_builder(self, tab_name):
        """
            build a tab link
        """
        url = self.root_url
        tab_link = url.split('/')
        tab_link.append('%s' % tab_name)
        tab_link = '/'.join(tab_link)
        return tab_link

    def content_link_builder(self, content, tab_name=None):
        """
            build content tab_edit link
            http://nohost/root/test_content/edit/tab_edit
        """
        url = self.root_url
        content_link = url.split('/')
        if tab_name:
            content_link.append('%s' % tab_name)
            content_link.insert(4, content)
            content_link = '/'.join(content_link)
        else:
            content_link.remove('edit')
            content_link.insert(4, content)
            content_link = '/'.join(content_link)
        return content_link

    def get_form_submit(self, browser, base_url, test_condition, form_name,
                        submit_value):
        """
            this is used when clicking onto a page that embeds a button in a
            form, like 'publish now' in the publish page
        """
        form = browser.getForm(name=form_name)
        self.failUnless(form_name in form.name, "test condition '%s' is not "
                        "the name of the form" % form_name)
        form.submit(submit_value)
        self.failUnless(test_condition in browser.contents, "test "
                        "condition '%s' is not included in browser content"
                        % test_condition)
        return browser.url

    def get_form(self, browser, base_url, form_name):
        ret = {}
        form = browser.getForm(name=form_name)
        self.failUnless(form_name in form.name, "test condition '%s' is not "
                        "the name of the form" % form_name)
        ret = {
            'url': browser.url,
            'form': form,
        }
        return ret

    def click_content_tab_name(self, browser, base_url, test_condition,
                               content, tab_name):
        """
            use this to click within content types
            example: host_name/root/test_content/edit/tab_name
        """
        link = self.content_link_builder(content, tab_name)
        link = browser.getLink(url=link)
        link_url = link.url
        self.assertEquals(link.url, '%s' % link_url)
        link.click()
        self.failUnless(test_condition in browser.contents, "test "
                        "condition '%s' is not included in browser content"
                        % test_condition)
        return browser.url

    def click_content_no_tab_name(self, browser, base_url, test_condition,
                                  content, link_text):
        """
            use this to click something like the 'view public version'
            example: host_name/root/test_content
        """
        link = self.content_link_builder(content)
        link = browser.getLink(text='%s' % link_text, url=link)
        link_url = link.url
        self.assertEquals(link.url, '%s' % link_url)
        link.click()
        self.failUnless(test_condition in browser.contents, "test "
                        "condition '%s' is not included in browser content"
                        % test_condition)

    def click_tab_name(self, browser, base_url, test_condition, tab_name):
        """
            use this to click around the root level of the smi
            example: host_name/root/edit/tab_name
        """
        link = self.tab_link_builder(tab_name)
        link = browser.getLink(url=link)
        link_url = link.url
        self.assertEquals(link.url, '%s' % link_url)
        link.click()
        self.failUnless(test_condition in browser.contents, "test "
                        "condition '%s' is not included in browser content"
                        % test_condition)

