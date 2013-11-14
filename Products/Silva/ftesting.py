# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import time
from Products.Silva.testing import tests


def rest_settings(browser):
    """Settings to test rest APIs.
    """
    # Cookie and redirect are required for the login form.
    browser.options.cookie_support = True
    browser.set_request_header('X-Requested-With', 'XMLHttpRequest')


def public_settings(browser):
    """Settings to test public views, using the standard issue skin.
    """
    # Cookie and redirect are required for the login form.
    browser.options.cookie_support = True
    browser.options.follow_redirect = True
    browser.options.follow_external_redirect = True
    browser.inspect.add(
        'title',
        css="div.box1 h1",
        type="text")
    browser.inspect.add(
        'navigation',
        css="div#sidebar a",
        type='link')
    browser.inspect.add(
        'content',
        css="div#content div.entry",
        type='text')


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

        def __init__(self, location):
            self.location = location

        def login(self, browser, user, password):
            browser.open(self.location + '/edit')

            form = browser.get_form('login_form')
            form.get_control('__ac.field.name').value = user
            form.get_control('__ac.field.password').value = password
            form.inspect.actions['log in'].click()
            tests.assertEqual(browser.location, self.location + '/edit')

        def logout(self, browser):
            browser.open(self.location + '/service_members/logout')

    def smi_click(browser, session, element, value):
        status = session.execute(
            """
if (window.smi)
   window.smi.ready.call(arguments[0]);
else
   arguments[0]();
""", [])
        # Wait an extra bit, for things like feedback to triggers.
        time.sleep(0.25)
        return status

    def page_open(browser, session):
        # Language should be english.
        browser.cookies.add('silva_language', 'en')
        return 200

    # Login support
    logger = LoginFormHandler('/root')
    browser.handlers.add('login', logger, False)
    browser.handlers.add('close', logger.logout)

    # Fix loading times
    browser.handlers.add('open', page_open)
    browser.handlers.add('onclick', smi_click)
    browser.handlers.add('onsubmit', smi_click)

    # Macros
    def set_datetime(browser, form, prefix, dt):
        # set a datetime field.
        mapping = {
            'day': lambda d: d.day,
            'month': lambda d: d.month,
            'year': lambda d: d.year,
            'hour': lambda d: d.hour,
            'min': lambda d: d.minute}

        for name, callback in mapping.items():
            control = form.get_control(".".join([prefix, name]))
            control.value = callback(dt)

    def assert_feedback(browser, message):
        # Verify we don't see any error message.
        tests.assertEqual(browser.inspect.error, [])
        # Verify we see the feedback message. click on it to close it.
        tests.assertEqual(browser.inspect.feedback, [message])
        tests.assertEqual(browser.inspect.feedback[0].close.click(), 200)
        tests.assertEqual(browser.inspect.feedback, [])

    def assert_error(browser, message):
        # Verify we don't see any feedback message.
        tests.assertEqual(browser.inspect.feedback, [])
        # Verify we see the error message. click on it to close it.
        tests.assertEqual(browser.inspect.error, [message])
        tests.assertEqual(browser.inspect.error[0].close.click(), 200)
        tests.assertEqual(browser.inspect.error, [])


    browser.macros.add('setDatetime', set_datetime)
    browser.macros.add('assertFeedback', assert_feedback)
    browser.macros.add('assertError', assert_error)

    # SMI
    browser.inspect.add(
        'tabs',
        css='div.metadata ol.content-tabs li.top-level',
        nested={None: ('name',),
                'name': {'css': 'a.top-entry',
                         'type': 'clickable',
                         'unique': True},
                'open': {'css': 'div.subtab-icon ins',
                         'type': 'clickable',
                         'unique': True},
                'entries': {'css': 'ol.subtabs li.sub-level a',
                            'type': 'clickable'}})
    browser.inspect.add(
        'activetabs',
        css="div.metadata ol.content-tabs a.active",
        type='link')
    browser.inspect.add(
        'views',
        css='div.metadata div.view-actions a',
        type='link')
    browser.inspect.add(
        'activeviews',
        css='div.metadata div.view-actions a.active',
        type='link')
    browser.inspect.add(
        'title',
        css='div.metadata h2',
        type='text',
        unique=True)
    browser.inspect.add(
        'parent',
        css="div.metadata div.admin-actions a.parent",
        type='link',
        unique=True)
    browser.inspect.add(
        'feedback',
        css='div.jGrowl-feedback',
        nested={
            None: ('message',),
            'message': {
                'css': 'div.jGrowl-message',
                'unique': True},
            'close': {
                'css': 'div.jGrowl-close',
                'type': 'clickable',
                'unique': True}})
    browser.inspect.add(
        'error',
        css='div.jGrowl-error',
        nested={
            None: ('message',),
            'message': {
                'css': 'div.jGrowl-message',
                'unique': True},
            'close': {
                'css': 'div.jGrowl-close',
                'type': 'clickable',
                'unique': True}})

    # Content toolbar actions
    browser.inspect.add(
        'toolbar',
        css='div.toolbar div.actions li a',
        type='clickable')
    # Folder listing
    browser.inspect.add(
        'listing_groups',
        xpath='//dl[@class="listing"]/dt',
        type='clickable')
    browser.inspect.add(
        'listing',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]',
        nested={
            None:  ('title', 'identifier', 'author'),
            'title': {
                'xpath': 'descendant::td[5]',
                'unique': True},
            'identifier': {
                'xpath': 'descendant::td[4]',
                'type': 'clickable',
                'unique': True},
            'modified': {
                'xpath': 'descendant::td[6]',
                'unique': True},
            'author': {
                'xpath': 'descendant::td[7]',
                'unique': True},
            'goto': {
                'xpath': 'descendant::td[8]/div/ol/li/a/span',
                'type': 'clickable',
                'unique': True},
            'goto_dropdown': {
                'xpath': 'descendant::td[8]//div[@class="dropdown-icon"]',
                'type': 'clickable',
                'unique': True},
            'goto_actions': {
                'xpath': 'descendant::td[8]//div[@class="dropdown"]//a',
                'type': 'clickable'}})

    # jQuery UI dialogs
    browser.inspect.add(
        'reference',
        css="a.reference-dialog-trigger",
        type='clickable')
    browser.inspect.add(
        'dialog',
        css="div.ui-dialog",
        nested={
            None: ('title',),
            'title': {
                'css': 'span.ui-dialog-title',
                'unique': True},
            'buttons': {
                'css': 'div.ui-dialog-buttonpane button.ui-button',
                'type': 'clickable'},
            'listing': {
                'css': 'table.source-list tr.item',
                'nested': {
                    None: ('identifier',),
                    'identifier': {
                        'css': 'td.item-id',
                        'type': 'clickable',
                        'unique': True},
                    'title': {
                        'css': 'td.item-title',
                        'unique': True},
                    'select': {
                        'css': 'td.actions img',
                        'type': 'clickable',
                        'unique': True}
                    }}})

    # Form
    browser.inspect.add(
        'form',
        css="form.form-fields-container",
        nested={
            None: ('title',),
            'title': {
                'xpath': 'descendant::div[@class="form-head"]/h3 | descendant::div[@class="form-head"]/h4',
                'unique': True},
            'form': {
                'type': 'form',
                'unique': True},
            'fields': {
                'type': 'form-fields',
                'unique': True},
            'actions': {
                'css': '.form-controls a',
                'type': 'clickable'}})


