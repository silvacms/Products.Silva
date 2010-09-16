# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


def smi_create_content(browser, content_type, **fields):
    """Create a content in SMI.
    """
    form = browser.get_form('md.container')
    assert content_type in form.controls['md.container.field.content'].options

    form.controls['md.container.field.content'].value = content_type
    assert form.controls['md.container.action.new'].click() ==  200

    # The add url is a + view with the content.
    assert browser.location.split('/')[-2:] == ['+', content_type]

    form = browser.get_form('addform')
    for name, value in fields.items():
        form.controls['addform.field.' + name].value = value

    assert form.controls['addform.action.save'].click() == 200
    assert browser.inspect.feedback == ['Added ' + content_type], \
        u"Unexpected feedback on add form: %s" % (
        ', '.join(browser.inspect.feedback))

    assert fields['id'] in browser.inspect.folder_listing


def smi_delete_content(browser, identifier):
    """Delete a content in SMI
    """
    assert identifier in browser.inspect.folder_listing

    form = browser.get_form('silvaObjects')
    form.get_control('ids:list').value = [identifier]

    assert form.get_control('tab_edit_delete:method').click() == 200
    assert browser.inspect.feedback == ['Deleted "%s".' % identifier], \
        u"Unexpected feedback on delete: %s" % (
        ', '.join(browser.inspect.feedback))


def smi_settings(browser):
    browser.inspect.add(
        'feedback',
        '//div[@id="feedback"]/div/span', type='text')
    # Top tabs navigation
    browser.inspect.add(
        'tabs',
        '//div[@class="tabs"]/a[contains(@class, "tab")]', type='link')
    # Second navigation (buttons in middleground)
    browser.inspect.add(
        'subtabs',
        '//div[@class="middleground"]/div[@class="transporter"]/a', type='link')
    # Breadcrumb
    browser.inspect.add(
        'breadcrumbs',
        '//div[@class="pathbar"]/a[@class="breadcrumb"]', type='link')
    # Sidebar navigation
    browser.inspect.add(
        'navigation_root',
        '(//div[@class="navigation"]//td)[1]/div/a', type='link')
    browser.inspect.add(
        'navigation',
        '//div[@class="navigation"]//td/div/a', type='link')
    # Container tab edit listing
    browser.inspect.add(
        'folder_listing',
        '//form[@name="silvaObjects"]/*/tbody/tr/td[2]/a[last()]', type='link')
    # Zeam Form errors
    browser.inspect.add(
        'form_errors',
        '//form[contains(@class,"zeam-form")]//div[@class="error"]',
        type='text')

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


    browser.macros.add('create', smi_create_content)
    browser.macros.add('delete', smi_delete_content)
