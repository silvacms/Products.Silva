#a -*- coding: utf-8 -*-
import os, sys, re
from os.path import join
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import SilvaTestCase
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.silvaxml import xmlexport
from Products.Silva.Link import manage_addLink
from Products.ParsedXML.ParsedXML import ParsedXML
from DateTime import DateTime

class SetTestCase(SilvaTestCase.SilvaTestCase):
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
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder)
        part1, part2, part3, part4, part5, part6, part7, part8, part9, part10 = splittor.split(exporter.exportToString(exportRoot, settings))
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="', part1)
        self.assertEquals('" path="/root/testfolder" silva_version="%s" url="http://nohost/root/testfolder"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">' % exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:modificationtime type="datetime">', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:modificationtime type="datetime">', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part8)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part9)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default></content></folder></content></folder></silva>', part10)


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
        testfolder2.test_link.set_unapproved_version_publication_datetime(DateTime() - 1)
        testfolder2.test_link.approve_version()
        testfolder3 = self.add_folder(
            self.root,
            'testfolder3',
            'This is yet &another; testfolder',
            policy_name='Auto TOC')
        manage_addGhost(
            testfolder3, 'caspar', '/root/testfolder/testfolder2/test_link')
        # export of a broken link
        manage_addGhost(
            testfolder3, 'sadcaspar', '/this_link_is_broken')

        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder3)
        part1, part2, part3, part4, part5, part6 = splittor.split(exporter.exportToString(exportRoot, settings))
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="', part1)
        self.assertEquals('" path="/root/testfolder3" silva_version="%s" url="http://nohost/root/testfolder3"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">' % exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:modificationtime type="datetime">', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part5)
        #self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><ghost id="caspar"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metatype>Silva Link</metatype><haunted_url>/root/testfolder/testfolder2/test_link</haunted_url><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part6)
        #self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:modificationtime type="datetime">', part7)
        #self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime type="datetime">', part8)
        #self.assertEquals( '</silva-extra:publicationtime><silva-extra:subject/></set></metadata><url>http://www.snpp.com/</url></content></content></ghost><ghost id="sadcaspar"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"/></ghost></content></folder></silva>', part9)
        
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

        # test broken ghost folder reference
        manage_addGhostFolder(
            testfolder3,
            'sadcaspar',
            '/root/testfolder/broken')
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder3)
        part1, part2, part3, part4, part5, part6, part7, part8, part9, part10 = splittor.split(exporter.exportToString(exportRoot, settings))
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="', part1)
        self.assertEquals('" path="/root/testfolder3" silva_version="%s" url="http://nohost/root/testfolder3"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">' % exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:modificationtime type="datetime">', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><ghost_folder id="caspar"><content><metatype>Silva Folder</metatype><haunted_url>/root/testfolder/testfolder2</haunted_url><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part8)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:modificationtime type="datetime">', part9)
        self.assertEquals(part10, '</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><url>http://www.snpp.com/</url></content></link></content></content></ghost_folder><ghost_folder id="sadcaspar"><content><metatype/><haunted_url>/root/testfolder/broken</haunted_url></content></folder></silva>')        
        
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
        # We will now do some horrible, horrible stuff to be able to test
        # the export, while ignoring the export date, which we can't know
        # about beforehand. Also I don't see how to get this within 80
        # columns without a lot of pain.
        splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder)
        part1, part2, part3, part4, part5, part6, part7, part8, part9, part10, part11, part12 = splittor.split(exporter.exportToString(exportRoot, settings))
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="', part1)
        self.assertEquals(
            '" path="/root/testfolder" silva_version="%s" url="http://nohost/root/testfolder"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">' %
            exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:modificationtime type="datetime">', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:modificationtime type="datetime">', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part8)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/index</silva-extra:location><silva-extra:modificationtime type="datetime">', part9)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime type="datetime">', part10)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:keywords/><silva-extra:lastauthor>unknown user</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:modificationtime type="datetime">', part11)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><url>http://www.snpp.com/</url></content></link></content></folder></content></folder></silva>', part12)

    def test_zip_export(self):
        from Products.Silva.silvaxml import xmlexport
        from Products.Silva.adapters import zipfileexport
        from Products.Silva.adapters import archivefileimport
        from Products.Silva.Image import Image
        from zipfile import ZipFile, BadZipfile
        directory = os.getcwd()
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
        zip_in = open(join(directory,'data','test.zip'))
        adapter = archivefileimport.getArchiveFileImportAdapter(testfolder2)
        succeeded, failed = adapter.importArchive(zip_in)
        get_transaction().commit(1)
        # we will now unregister the image producer, to test whether 
        # fallback kicks in
        xmlexport.theXMLExporter._mapping[Image] = None
        settings = xmlexport.ExportSettings()
        adapter = zipfileexport.getZipfileExportAdapter(testfolder)
        result = adapter.exportToZip(testfolder, settings)
        f = open('test_export.zip', 'wb')
        f.write(result)
        f.close()
        f = open('test_export.zip', 'rb')
        zip_out = ZipFile(f, 'r')
        namelist = zip_out.namelist()
        namelist.sort()
        self.assertEquals(
            ['assets/1', 'assets/2', 'silva.xml', 'zexps/1.zexp', 
            'zexps/2.zexp', 'zexps/3.zexp', 'zexps/4.zexp', 'zexps/5.zexp'], 
            namelist)
        zip_out.close()
        f.close()
        os.remove('test_export.zip')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SetTestCase))
        return suite
