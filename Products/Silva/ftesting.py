# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import time
import transaction


def public_settings(browser):
    browser.inspect.add(
        'title',
        css="h1",
        type="text")

def zmi_settings(browser):
    # ZMI
    browser.inspect.add(
        'zmi_tabs',
        '//td[@class="tab-small"]//a',
        type='link')
    browser.inspect.add(
        'zmi_listing',
        '//tr[@class="row-hilite" or @class="row-normal"]'
        '//div[@class="list-item"]/a',
        type='link')
    browser.inspect.add(
        'zmi_title',
        '//h2')
    browser.inspect.add(
        'zmi_feedback',
        '//div[@class="system-msg"]')
    browser.inspect.add(
        'zmi_status',
        '//p[@class="system-msg"]')

def smi_settings(browser):
    zmi_settings(browser)

    class LoginFormHandler(object):

        def __init__(self, smi_url):
            self.smi_url = smi_url

        def login(self, browser, user, password):
            browser.open(self.smi_url + '/edit')

            form = browser.get_form('login_form')
            form.get_control('__ac.field.name').value = user
            form.get_control('__ac.field.password').value = password

            form.inspect.actions['log in'].click()

            assert browser.location == self.smi_url + '/edit'

        def logout(self, browser):
            browser.open(self.smi_url + '/service_members/logout')


    def commit_local_changes(*args):
        transaction.commit()

    def wait_for_smi(browser, session, element, value):
        return session.execute(
            """
if (window.smi)
   window.smi.ready.call(arguments[0]);
else
   arguments[0]();
""", [])

    def wait_for_initial_smi(browser, session):
        time.sleep(0.5)

    # Login support
    logger = LoginFormHandler('/root')
    browser.handlers.add('login', logger, False)
    browser.handlers.add('close', logger.logout)

    commit_local_changes()
    browser.handlers.add('open', wait_for_initial_smi)

    browser.handlers.add('onclick', wait_for_smi)
    browser.handlers.add('onsubmit', wait_for_smi)

    # Macros
    def set_datetime(browser, form, prefix, dt):
        mapping = {
            'day': lambda d: d.day,
            'month': lambda d: d.month,
            'year': lambda d: d.year,
            'hour': lambda d: d.hour,
            'min': lambda d: d.minute}

        for name, callback in mapping.items():
            control = form.get_control(".".join([prefix, name]))
            control.value = callback(dt)

    browser.macros.add('set_datetime', set_datetime)

    # SMI
    browser.inspect.add(
        'content_tabs',
        css='div.metadata ol.content-tabs a.top-entry',
        type='link')
    browser.inspect.add(
        'content_subtabs',
        css='div.metadata ol.content-tabs ol a.open-screen',
        type='link')
    browser.inspect.add(
        'content_activetabs',
        css="div.metadata ol.content-tabs a.active",
        type='link')
    browser.inspect.add(
        'content_views',
        css='div.metadata div.view-actions a',
        type='link')
    browser.inspect.add(
        'content_activeviews',
        css='div.metadata div.view-actions a.active',
        type='link')
    browser.inspect.add(
        'content_title',
        css='div.metadata h2',
        type='text')
    browser.inspect.add(
        'content_parent',
        css="div.metadata div.admin-actions a.parent",
        type='link')
    browser.inspect.add(
        'feedback',
        css='div.notification p')

    # Folder listing

    browser.inspect.add(
        'folder_identifier',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[3]')
    browser.inspect.add(
        'folder_title',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[4]')
    browser.inspect.add(
        'folder_modified',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[5]')
    browser.inspect.add(
        'folder_author',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[6]')

    browser.inspect.add(
        'folder_goto',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[7]/div/ol/li/a/span',
        type='clickable')
    browser.inspect.add(
        'folder_goto_dropdown',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[7]//div[@class="dropdown-icon"]',
        type='clickable')
    browser.inspect.add(
        'folder_goto_actions',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]/td[7]//div[@class="dropdown"]/a',
        type='clickable')

    browser.inspect.add(
        'folder',
        compound={'title': 'folder_title',
                  'identifier': 'folder_identifier',
                  'modified': 'folder_modified',
                  'author': 'folder_author',
                  'goto': 'folder_goto',
                  'goto_dropdown': 'folder_goto_dropdown'})

    browser.inspect.add(
        'folder_publishables_identifier',
        xpath='//dl[@class="listing"]/dd[@class="publishables"]//tr[@class="item"]/td[3]')
    browser.inspect.add(
        'folder_publishables_title',
        xpath='//dl[@class="listing"]/dd[@class="publishables"]//tr[@class="item"]/td[4]')
    browser.inspect.add(
        'folder_publishables_modified',
        xpath='//dl[@class="listing"]/dd[@class="publishables"]//tr[@class="item"]/td[5]')
    browser.inspect.add(
        'folder_publishables_author',
        xpath='//dl[@class="listing"]/dd[@class="publishables"]//tr[@class="item"]/td[6]')

    browser.inspect.add(
        'folder_assets_identifier',
        xpath='//dl[@class="listing"]/dd[@class="assets"]//tr[@class="item"]/td[3]')
    browser.inspect.add(
        'folder_assets_title',
        xpath='//dl[@class="listing"]/dd[@class="assets"]//tr[@class="item"]/td[4]')
    browser.inspect.add(
        'folder_assets_modified',
        xpath='//dl[@class="listing"]/dd[@class="assets"]//tr[@class="item"]/td[5]')
    browser.inspect.add(
        'folder_assets_author',
        xpath='//dl[@class="listing"]/dd[@class="assets"]//tr[@class="item"]/td[6]')

    # Form
    browser.inspect.add(
        'form_controls',
        css="div.form-controls a",
        type='link')



# def smi_create_content(browser, content_type, **fields):
#     """Create a content in SMI.
#     """
#     form = browser.get_form('md.container')
#     assert content_type in form.controls['md.container.field.content'].options

#     form.controls['md.container.field.content'].value = content_type
#     assert form.controls['md.container.action.new'].click() ==  200

#     # The add url is a + view with the content.
#     assert browser.location.split('/')[-2:] == ['+', content_type]

#     form = browser.get_form('addform')
#     for name, value in fields.items():
#         form.controls['addform.field.' + name].value = value

#     assert form.controls['addform.action.save'].click() == 200
#     assert browser.inspect.feedback == ['Added ' + content_type + '.'], \
#         u"Unexpected feedback on add form: %s" % (
#         ', '.join(browser.inspect.feedback))

#     assert fields['id'] in browser.inspect.folder_listing


# def smi_delete_content(browser, identifier):
#     """Delete a content in SMI
#     """
#     assert identifier in browser.inspect.folder_listing

#     form = browser.get_form('silvaObjects')
#     form.get_control('ids:list').value = [identifier]

#     assert form.get_control('tab_edit_delete:method').click() == 200
#     assert browser.inspect.feedback == ['Deleted "%s".' % identifier], \
#         u"Unexpected feedback on delete: %s" % (
#         ', '.join(browser.inspect.feedback))


# def smi_settings(browser):
#     browser.inspect.add(
#         'feedback',
#         '//div[@id="feedback"]/div/span', type='text')
#     # Top tabs navigation
#     browser.inspect.add(
#         'tabs',
#         '//div[@class="tabs"]/a[contains(@class, "tab")]', type='link')
#     # Second navigation (buttons in middleground)
#     browser.inspect.add(
#         'subtabs',
#         '//div[@class="middleground"]/div[@class="transporter"]/a', type='link')
#     # Breadcrumb
#     browser.inspect.add(
#         'breadcrumbs',
#         '//div[@class="pathbar"]/a[contains(@class, "breadcrumb")]', type='link')
#     # Sidebar navigation
#     browser.inspect.add(
#         'navigation_root',
#         '(//div[@class="navigation"]//td)[1]/div/a', type='link')
#     browser.inspect.add(
#         'navigation',
#         '//div[@class="navigation"]//td/div/a', type='link')
#     # Container tab edit listing
#     browser.inspect.add(
#         'folder_listing',
#         '//form[@name="silvaObjects"]/*/tbody/tr/td[2]/a[last()]', type='link')
#     # Zeam Form errors
#     browser.inspect.add(
#         'form_errors',
#         '//form[contains(@class,"zeam-form")]//div[@class="error"]',
#         type='text')

#     zmi_settings(browser)

#     browser.macros.add('create', smi_create_content)
#     browser.macros.add('delete', smi_delete_content)
