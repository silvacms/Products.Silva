# -*- coding: utf-8 -*-
import os, sys, re
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.SilvaDocument.Document import manage_addDocument
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.adapters import xmlexport
from Products.Silva.Link import manage_addLink
from Products.ParsedXML.ParsedXML import ParsedXML

class SetTestCase(SilvaTestCase.SilvaTestCase):

    def test_xml_document_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        manage_addDocument(
            testfolder, 'test_document', 'This is (surprise!) a document')
        doc = testfolder.test_document
        doc_edit = doc.get_editable()
        doc_edit.content = ParsedXML(
            'test_document',
            """<?xml version="1.0" encoding="utf-8"?><doc>
            <node foo="bar">承諾広告＊既に、２億、３億、５億９千万円収入者が続出<node2>boo</node2>
            baz</node></doc>""")
        xmlexport.initializeXMLSourceRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        part1, part2 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, """"><folder id="testfolder"><document id="test_document"><workflow><version id="0"><status>unapproved</status><publication_date></publication_date><expiration_date></expiration_date></version></workflow><versions><document_version version_id="0"><title></title><doc>
            <node foo="bar">承諾広告＊既に、２億、３億、５億９千万円収入者が続出<node2>boo</node2>
            baz</node></doc></document_version></versions></document></folder></silva>""")

    def test_xml_folder_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Auto TOC')
        xmlexport.initializeXMLSourceRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        part1, part2 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder"><folder id="testfolder2"></folder></folder></silva>')

    def test_xml_ghost_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Auto TOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        testfolder3 = self.add_folder(
            self.root,
            'testfolder3',
            'This is yet &another; testfolder',
            policy_name='Auto TOC')
        manage_addGhost(
            testfolder3, 'caspar', '/root/testfolder/testfolder2/test_link')
        xmlexport.initializeXMLSourceRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        part1, part2, part3, part4 = splittor.split(xmlexport.getXMLSource(testfolder3).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" path="/root/testfolder3" url="http://nohost/root/testfolder3" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder3"><ghost id="caspar"><workflow><version id="0"><status>unapproved</status><publication_date></publication_date><expiration_date></expiration_date></version></workflow><versions><version version_id="0"><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_date></publication_date><expiration_date></expiration_date></version></workflow><versions><version version_id="0"><metadata><title></title><set xmlns="http://infrae.com/namespaces/metadata/silva"><maintitle>This is a test link, you insensitive clod!</maintitle><shorttitle></shorttitle></set><set xmlns="http://infrae.com/namespaces/metadata/silva-extra"><subject></subject><expirationtime></expirationtime><keywords></keywords><publicationtime></publicationtime><location>http://nohost/root/testfolder/testfolder2/test_link</location><contactemail></contactemail><modificationtime>')
        self.assertEquals(part3, '</modificationtime><creationtime>')
        self.assertEquals(part4, '</creationtime><lastauthor>unknown user</lastauthor><creator>test_user_1_</creator><contactname></contactname><content_description></content_description><comment></comment></set></metadata><url>http://www.snpp.com/</url></version></versions></link></version></versions></ghost></folder></silva>')

    def test_xml_ghost_folder_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Auto TOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        testfolder3 = self.add_folder(
            self.root,
            'testfolder3',
            'This is yet &another; testfolder',
            policy_name='Auto TOC')
        manage_addGhostFolder(
            testfolder3,
            'caspar',
            '/root/testfolder/testfolder2')
        xmlexport.initializeXMLSourceRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        part1, part2, part3, part4 = splittor.split(xmlexport.getXMLSource(testfolder3).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" path="/root/testfolder3" url="http://nohost/root/testfolder3" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder3"><ghost_folder id="caspar"><folder id="testfolder2"><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_date></publication_date><expiration_date></expiration_date></version></workflow><versions><version version_id="0"><metadata><title></title><set xmlns="http://infrae.com/namespaces/metadata/silva"><maintitle>This is a test link, you insensitive clod!</maintitle><shorttitle></shorttitle></set><set xmlns="http://infrae.com/namespaces/metadata/silva-extra"><subject></subject><expirationtime></expirationtime><keywords></keywords><publicationtime></publicationtime><location>http://nohost/root/testfolder/testfolder2/test_link</location><contactemail></contactemail><modificationtime>')
        self.assertEquals(part3, '</modificationtime><creationtime>')
        self.assertEquals(part4, '</creationtime><lastauthor>unknown user</lastauthor><creator>test_user_1_</creator><contactname></contactname><content_description></content_description><comment></comment></set></metadata><url>http://www.snpp.com/</url></version></versions></link></folder></ghost_folder></folder></silva>')

    def test_xml_link_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Auto TOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Auto TOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        xmlexport.initializeXMLSourceRegistry()
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        part1, part2, part3, part4 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder"><folder id="testfolder2"><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_date></publication_date><expiration_date></expiration_date></version></workflow><versions><version version_id="0"><metadata><title></title><set xmlns="http://infrae.com/namespaces/metadata/silva"><maintitle>This is a test link, you insensitive clod!</maintitle><shorttitle></shorttitle></set><set xmlns="http://infrae.com/namespaces/metadata/silva-extra"><subject></subject><expirationtime></expirationtime><keywords></keywords><publicationtime></publicationtime><location>http://nohost/root/testfolder/testfolder2/test_link</location><contactemail></contactemail><modificationtime>')
        self.assertEquals(part3, '</modificationtime><creationtime>')
        self.assertEquals(part4, '</creationtime><lastauthor>unknown user</lastauthor><creator>test_user_1_</creator><contactname></contactname><content_description></content_description><comment></comment></set></metadata><url>http://www.snpp.com/</url></version></versions></link></folder></folder></silva>')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite