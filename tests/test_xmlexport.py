# -*- coding: utf-8 -*-
import os, sys, re
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.SilvaDocument.Document import manage_addDocument
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.silvaxml import xmlexport
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
        part1, part2, part3, part4, part5, part6 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part3, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part4, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><document id="test_document"><workflow><version id="0"><status>unapproved</status><publication_datetime></publication_datetime><expiration_datetime></expiration_datetime></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is (surprise!) a document</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/test_document</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part5, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part6, """</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><doc>
            <node foo="bar">承諾広告＊既に、２億、３億、５億９千万円収入者が続出<node2>boo</node2>
            baz</node></doc></content></document></content></folder></silva>""")
            
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
        part1, part2, part3, part4, part5, part6 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part3, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part4, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part5, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part6, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content></content></folder></content></folder></silva>')

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
        part1, part2, part3, part4, part5, part6 = splittor.split(xmlexport.getXMLSource(testfolder3).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" path="/root/testfolder3" url="http://nohost/root/testfolder3" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part3, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part4, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><ghost id="caspar"><workflow><version id="0"><status>unapproved</status><publication_datetime></publication_datetime><expiration_datetime></expiration_datetime></version></workflow><content version_id="0"><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime></publication_datetime><expiration_datetime></expiration_datetime></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part5, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part6, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><url>http://www.snpp.com/</url></content></link></content></ghost></content></folder></silva>')
        
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
        part1, part2, part3, part4, part5, part6, part7, part8 = splittor.split(xmlexport.getXMLSource(testfolder3).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" path="/root/testfolder3" url="http://nohost/root/testfolder3" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part3, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part4, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><ghost_folder id="caspar"><content><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part5, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part6, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime></publication_datetime><expiration_datetime></expiration_datetime></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part7, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part8, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><url>http://www.snpp.com/</url></content></link></content></folder></content></ghost_folder></content></folder></silva>')

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
        part1, part2, part3, part4, part5, part6, part7, part8 = splittor.split(xmlexport.getXMLSource(testfolder).xmlToString(None))
        self.assertEquals(part1, '<silva xmlns="http://infrae.com/ns/silva/0.5" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" path="/root/testfolder" url="http://nohost/root/testfolder" datetime="')
        self.assertEquals(part2, '"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part3, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part4, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part5, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part6, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><content><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime></publication_datetime><expiration_datetime></expiration_datetime></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle></silva-content:shorttitle></set><set id="silva-extra"><silva-extra:subject></silva-extra:subject><silva-extra:expirationtime></silva-extra:expirationtime><silva-extra:keywords></silva-extra:keywords><silva-extra:publicationtime></silva-extra:publicationtime><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:contactemail></silva-extra:contactemail><silva-extra:modificationtime>')
        self.assertEquals(part7, '</silva-extra:modificationtime><silva-extra:creationtime>')
        self.assertEquals(part8, '</silva-extra:creationtime><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:contactname></silva-extra:contactname><silva-extra:content_description></silva-extra:content_description><silva-extra:comment></silva-extra:comment></set></metadata><url>http://www.snpp.com/</url></content></link></content></folder></content></folder></silva>')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite