# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import time


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

        def __init__(self, url):
            self.url = url

        def login(self, browser, user, password):
            browser.open(self.url + '/edit')

            form = browser.get_form('login_form')
            form.get_control('__ac.field.name').value = user
            form.get_control('__ac.field.password').value = password
            form.inspect.actions['log in'].click()

            assert browser.location == self.url + '/edit'

        def logout(self, browser):
            browser.open(self.url + '/service_members/logout')

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
        'tabs',
        css='div.metadata ol.content-tabs a.top-entry',
        type='link')
    browser.inspect.add(
        'subtabs',
        css='div.metadata ol.content-tabs ol a.open-screen',
        type='link')
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
        css='div.jGrowl-message')

    # Content actions
    browser.inspect.add(
        'actions',
        css='div.toolbar div.actions li a',
        type='clickable')
    # Folder listing
    browser.inspect.add(
        'listing',
        xpath='//dl[@class="listing"]//tr[contains(@class,"item")]',
        nested={
            None:  ('title', 'identifier', 'author'),
            'title': {
                'xpath': '//td[5]',
                'unique': True},
            'identifier': {
                'xpath': '//td[4]',
                'type': 'clickable',
                'unique': True},
            'modified': {
                'xpath': '//td[6]',
                'unique': True},
            'author': {
                'xpath': '//td[7]',
                'unique': True},
            'goto': {
                'xpath': '//td[8]/div/ol/li/a/span',
                'type': 'clickable',
                'unique': True},
            'goto_dropdown': {
                'xpath': '//td[8]//div[@class="dropdown-icon"]',
                'type': 'clickable',
                'unique': True},
            'goto_actions': {
                'xpath': '//td[8]//div[@class="dropdown"]/a',
                'type': 'clickable'}})
    # jQuery UI dialogs
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
                'type': 'clickable'}})

    # Form
    browser.inspect.add(
        'form_controls',
        css="div.form-controls a",
        type='link')


