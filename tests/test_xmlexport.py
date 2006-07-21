# Python
import os
import re
from os.path import join
from zipfile import ZipFile, BadZipfile

import SilvaTestCase
from SilvaTestCase import transaction
# Zope
from Products.ParsedXML.ParsedXML import ParsedXML
from DateTime import DateTime
# Silva
from Products.Silva.Ghost import manage_addGhost
from Products.Silva.GhostFolder import manage_addGhostFolder
from Products.Silva.silvaxml import xmlexport
from Products.Silva.Link import manage_addLink
from Products.Silva.adapters import zipfileexport, archivefileimport, xmlsource
from Products.Silva.Image import Image

class SetTestCase(SilvaTestCase.SilvaTestCase):
    DATETIME_RE = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
    def replace_datetimes(self, s):
        return self.DATETIME_RE.sub(r'YYYY-MM-DDTHH:MM:SS', s)
    
    def test_xml_folder_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
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
        self.assertEquals('" path="/root/testfolder" silva_version="%s" url="http://nohost/root/testfolder"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>' % exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:modificationtime>', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/index</silva-extra:location><silva-extra:modificationtime>', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:modificationtime>', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part8)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/index</silva-extra:location><silva-extra:modificationtime>', part9)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default></content></folder></content></folder></silva>', part10)

    def test_xml_ghost_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
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
            policy_name='Silva AutoTOC')
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
        part1, part2, part3, part4, part5, part6, part7, part8, part9 = splittor.split(
            exporter.exportToString(exportRoot, settings))
        self.assertEquals('<?xml version="1.0" encoding="utf-8"?>\n<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="', part1)
        self.assertEquals('" path="/root/testfolder3" silva_version="%s" url="http://nohost/root/testfolder3"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>' % exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:modificationtime>', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3/index</silva-extra:location><silva-extra:modificationtime>', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><ghost id="caspar"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metatype>Silva Link</metatype><haunted_url>/root/testfolder/testfolder2/test_link</haunted_url><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>unknown</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:modificationtime>', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime>', part8)
        self.assertEquals('</silva-extra:publicationtime><silva-extra:subject/></set></metadata><url>http://www.snpp.com/</url></content></content></ghost><ghost id="sadcaspar"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metatype/><haunted_url>/this_link_is_broken</haunted_url></content></ghost></content></folder></silva>', part9)
        
    def test_xml_ghost_folder_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        testfolder3 = self.add_folder(
            self.root,
            'testfolder3',
            'This is yet &another; testfolder',
            policy_name='Silva AutoTOC')
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
        #splittor = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
        settings = xmlexport.ExportSettings()
        exporter = xmlexport.theXMLExporter
        exportRoot = xmlexport.SilvaExportRoot(testfolder3)
        xml = self.replace_datetimes(exporter.exportToString(exportRoot, settings))
        self.assertEquals(
            xml,
            '''\
<?xml version="1.0" encoding="utf-8"?>
<silva xmlns="http://infrae.com/ns/silva" xmlns:doc="http://infrae.com/ns/silva_document" xmlns:silva-content="http://infrae.com/namespaces/metadata/silva" xmlns:silva-extra="http://infrae.com/namespaces/metadata/silva-extra" datetime="YYYY-MM-DDTHH:MM:SS" path="/root/testfolder3" silva_version="Silva 1.6b2" url="http://nohost/root/testfolder3"><folder id="testfolder3"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>YYYY-MM-DDTHH:MM:SS</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3</silva-extra:location><silva-extra:modificationtime>YYYY-MM-DDTHH:MM:SS</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is yet &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>YYYY-MM-DDTHH:MM:SS</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder3/index</silva-extra:location><silva-extra:modificationtime>YYYY-MM-DDTHH:MM:SS</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><ghost_folder id="caspar"><content><metatype>Silva Folder</metatype><haunted_url>/root/testfolder/testfolder2</haunted_url></content></ghost_folder><ghost_folder id="sadcaspar"><content><metatype/><haunted_url>/root/testfolder/broken</haunted_url></content></ghost_folder></content></folder></silva>''')

    def test_xml_link_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
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
            '" path="/root/testfolder" silva_version="%s" url="http://nohost/root/testfolder"><folder id="testfolder"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>' %
            exportRoot.getSilvaProductVersion(), part2)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder</silva-extra:location><silva-extra:modificationtime>', part3)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &lt;boo&gt;a&lt;/boo&gt; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part4)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/index</silva-extra:location><silva-extra:modificationtime>', part5)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><folder id="testfolder2"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part6)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>n/a</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2</silva-extra:location><silva-extra:modificationtime>', part7)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><content><default><auto_toc id="index"><metadata><set id="silva-content"><silva-content:maintitle>This is &amp;another; testfolder</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part8)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>test_user_1_</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/index</silva-extra:location><silva-extra:modificationtime>', part9)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata></auto_toc></default><link id="test_link"><workflow><version id="0"><status>unapproved</status><publication_datetime/><expiration_datetime/></version></workflow><content version_id="0"><metadata><set id="silva-content"><silva-content:maintitle>This is a test link, you insensitive clod!</silva-content:maintitle><silva-content:shorttitle/></set><set id="silva-extra"><silva-extra:comment/><silva-extra:contactemail/><silva-extra:contactname/><silva-extra:content_description/><silva-extra:creationtime>', part10)
        self.assertEquals('</silva-extra:creationtime><silva-extra:creator>test_user_1_</silva-extra:creator><silva-extra:expirationtime/><silva-extra:hide_from_tocs>do not hide</silva-extra:hide_from_tocs><silva-extra:keywords/><silva-extra:language/><silva-extra:lastauthor>unknown</silva-extra:lastauthor><silva-extra:location>http://nohost/root/testfolder/testfolder2/test_link</silva-extra:location><silva-extra:modificationtime>', part11)
        self.assertEquals('</silva-extra:modificationtime><silva-extra:publicationtime/><silva-extra:subject/></set></metadata><url>http://www.snpp.com/</url></content></link></content></folder></content></folder></silva>', part12)

    def test_xml_folder_with_assets_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        directory = os.path.dirname(__file__)
        zip_in = open(join(directory,'data','test1.zip'))
        adapter = archivefileimport.getArchiveFileImportAdapter(testfolder2)
        succeeded, failed = adapter.importArchive(zip_in)
        transaction.get().commit(1)
        # We just see if we can call the 'getXML()' on the xmlsource adapter
        # without failure. This will test/prove that we *do* need to provide
        # an ExportInfo object to the exporter.exportToString() in the
        # xmlsource adapter.
        adapted = xmlsource.getXMLSourceAdapter(testfolder)
        self.assert_(adapted.getXML())

    def test_zip_export(self):
        testfolder = self.add_folder(
            self.root,
            'testfolder',
            'This is <boo>a</boo> testfolder',
            policy_name='Silva AutoTOC')
        testfolder2 = self.add_folder(
            testfolder,
            'testfolder2',
            'This is &another; testfolder',
            policy_name='Silva AutoTOC')
        manage_addLink(
            testfolder2,
            'test_link',
            'This is a test link, you insensitive clod!',
            'http://www.snpp.com/')
        directory = os.path.dirname(__file__)
        zip_in = open(join(directory,'data','test1.zip'))
        adapter = archivefileimport.getArchiveFileImportAdapter(testfolder2)
        succeeded, failed = adapter.importArchive(zip_in)
        transaction.get().commit(1)
        # we will now unregister the image producer, to test whether 
        # fallback kicks in
        xmlexport.theXMLExporter._mapping[Image] = None
        settings = xmlexport.ExportSettings()
        adapter = zipfileexport.getZipfileExportAdapter(testfolder)
        result = adapter.exportToZip(testfolder, settings)
        f = open(join(directory, 'test_export.zip'), 'wb')
        f.write(result)
        f.close()
        f = open(join(directory, 'test_export.zip'), 'rb')
        zip_out = ZipFile(f, 'r')
        namelist = zip_out.namelist()
        namelist.sort()
        self.assertEquals(
            ['assets/1', 'assets/2', 'silva.xml', 'zexps/1.zexp', 
            'zexps/2.zexp', 'zexps/3.zexp', 'zexps/4.zexp', 'zexps/5.zexp'], 
            namelist)
        zip_out.close()
        f.close()
        os.remove(join(directory, 'test_export.zip'))

import unittest
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SetTestCase))
    return suite
