# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
#
# Testing of xml<->xhtml bidrectional conversions.
# this tests along with the module is intended to 
# work with python2.1 and python2.2 or better
# 

# $Revision: 1.3 $
import unittest

# 
# module setup
#

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO 

try:
    from xml.parsers import expat 
except ImportError:
    from xml.parsers.pyexpat import expat

import sys,os

try:
    sys.path.append('../../..')
    from transform.eopro3_0 import silva
    from transform.eopro3_0 import html
    from transform.Transformer import Transformer, EditorTransformer
except ImportError:
    import Zope
    from Products.Silva.transform.eopro3_0 import silva, html
    from Products.Silva.transform.Transformer import Transformer, EditorTransformer

# lazy, but in the end we want to test everything anyway

from xml.dom import minidom

class Base(unittest.TestCase):
    """ Check various conversions/transformations """

    def setUp(self):
        self.transformer = EditorTransformer('eopro3_0')

    def parse_silvafrag(self, frag):
        s = '<doc>%s</doc>' % frag
        node = self.transformer.source_parser.parse(s)
        return node.find_one('doc').find()

    def parse_htmlfrag(self, html_frag):

        s = '<body>%s</body>' % html_frag

        node = self.transformer.target_parser.parse(s)
        return node.find_one('body').find()

    def htmlfrag_to_silvadocument(self, html_frag):
        s = """<html>
                   <head>
                       <meta name="id" content="test"/>
                       <meta name="title" content="test title"/>
                       <title>test title</title>
                   </head>

                   <body>%(html_frag)s</body>
                   </html>""" % locals()

        nodes = self.parse_htmlfrag(s)
        self.assertEquals(len(self.transformer.target_parser.unknown_tags), 0)
        # convert to silva
        cnodes = nodes.conv()
        return cnodes.find_one('silva_document')

class HTML2XML(Base):
    """ test conversions from HTML to XML """
    context = {'id': 'test', 'title':'testtitle'}

    def test_basic_silva_structure(self):
        silvadoc = self.htmlfrag_to_silvadocument("<h3>title</h3>")
        self.assertEquals(silvadoc.attrs.get('id'), 'test')
        title = silvadoc.find_one('title')
        self.assertEquals(title.extract_text(), 'test title')
        doc = silvadoc.find('doc')
        self.assertEquals(len(doc), 1)

    def _check_heading(self, htag, stype, htag_back=None):
        if htag_back is None:
            htag_back = htag

        html_frag = "<%(htag)s>eins</%(htag)s>" % locals()
        htmlnode = self.parse_htmlfrag(html_frag)

        silvanode = htmlnode.conv()

        # check that conversion to silva works
        heading = silvanode.find('heading')
        self.assertEquals(len(heading), 1)
        heading = heading[0]
        self.assertEquals(heading.attrs.get('type'), stype)

        # check that conversion to back to html works
        backnode = silvanode.conv()
        hx = backnode.find(htag_back)
        self.assertEquals(len(hx), 1)

    def test_h3(self):
        self._check_heading('h3', 'normal')

    def test_h4(self):
        self._check_heading('h4', 'sub')

    def test_h5(self):
        self._check_heading('h5', 'subsub')

    def test_h6(self):
        self._check_heading('h6', 'paragraph')

    def test_dlist_simple(self):
        s = '''<ul type="none">
                   <li><term>term1</term><desc>desc1</desc></li>
               </ul>
            '''
        htmlnode = self.parse_htmlfrag(s)
        sn = htmlnode.conv()
        dlist = sn.find_one('dlist') 
        dt = dlist.find_one('dt')
        dd = dlist.find_one('dd')

    def test_dlist_broken_desc(self):
        s = '''<ul type="none">
                   <li><term>term1</term></li>
               </ul>
            '''
        htmlnode = self.parse_htmlfrag(s)
        sn = htmlnode.conv()
        dlist = sn.find_one('dlist') 
        dt = dlist.find_one('dt')
        dd = dlist.find_one('dd')
        self.assertEquals(dd.extract_text(), '')

    def _test_default_heading_conversion_h1(self):
        html_frag="""<body><h1>eins</h1></body>"""
        htmlnode = self.transformer.target_parser.parse(html_frag)
        self.assert_(not self.transformer.target_parser.unknown_tags)
        node = htmlnode.convert(context={'id':u'', 'title':u''})
        doc = node.find('silva_document')[0].find('doc')[0]
        heading = doc.find('heading')
        self.assertEquals(len(heading), 1)
        self.assertEquals(heading[0].attrs.get('type'), 'normal')

    def _test_ol_list_conversion(self):
        html_frag="""<ol><li>eins</li><li>zwei</li></ol>"""
        node = self.transformer.target_parser.parse(html_frag)
        self.assert_(not self.transformer.target_parser.unknown_tags)
        #node = node.find('body')[0]
        node = node.find('ol')
        list_node = node.conv()
        self.assertEquals(len(list_node),1)
        list_node = list_node[0]
        self.assert_(list_node.name()=='list')
        self.assert_(list_node.attrs.has_key('type'))
        self.assert_(list_node.attrs['type']=='1')
        self.assert_(len(list_node.find('li'))==2)

    def _test_ignore_html(self):
        """ test that a html tag doesn't modify the silva-outcome """
        frag="""<body silva_id="test"><h2 silva_id="test">titel</h2><h3>titel</h3></body>"""
        node = self.transformer.target_parser.parse(frag)
        node = node.conv()

        frag2="""<html><head></head>%(frag)s</html>""" % locals()
        node2 = self.transformer.target_parser.parse(frag2)
        node2 = node2.conv()

        self.assertEquals(node, node2)

    def _test_image_within_p_turns_outside(self):
        frag="""<p>hallo<img src="/path/to/image"/>dies</p>"""
        node = self.transformer.target_parser.parse(frag)
        node = node.convert(self.context)

        p = node.find('p')
        self.assert_(len(p)==2)
        image = node.find('image')
        self.assert_(len(image)==1)
        self.assert_(p[0].content.asBytes()=='hallo')
        self.assert_(p[1].content.asBytes()=='dies')

    def test_empty_paras_are_preserved(self):
        frag="""<p>hallo</p><p></p><p></p>"""
        node = self.parse_htmlfrag(frag)
        doc = node.convert(self.context)
        p = doc.find('p')
        self.assert_(len(p)==3)
        self.assert_(p[0].content.asBytes()=='hallo')
        self.assert_(not p[1].content.asBytes())
        self.assert_(not p[2].content.asBytes())

    def _test_image_simple(self):
        htmlfrag="""<img src="/silva/path/image" link="http://www.heise.de" align="float-left"/>"""
        node = self.transformer.target_parser.parse(htmlfrag)

        node = node.conv()
        self.assertEquals(len(node),1)
        img = node[0]
        self.assertEquals(img.name(), 'image')
        self.assertEquals(img.attrs.get('path'), '/silva/path')
        self.assertEquals(img.attrs.get('link'), 'http://www.heise.de')
        node = node.conv()
        self.assertEquals(len(node),1)
        img = node[0]
        self.assertEquals(img.attrs.get('src'), '/silva/path/image')
        self.assertEquals(img.attrs.get('link'), 'http://www.heise.de')

    def _test_image_URL_stripping(self):
        frag="""<img src="http://asd:123/silva/path/image"/>"""
        node = self.transformer.target_parser.parse(frag)

        img = node.conv()
        self.assertEquals(len(img),1)
        img = img[0]
        self.assertEquals(img.attrs.get('path'), '/silva/path')

    def test_nested_list_conversion_works_with_titles(self):
        frag="""<ul><li>one</li>
                    <ol><li>nested item</li></ol>
                </ul>"""
        node = self.transformer.target_parser.parse(frag)
        node = node.conv()

        #print "result of conversion"
        #print node.asBytes()
        #print "-------"

        nlist = node.find('nlist')
        self.assertEquals(len(nlist),1)
        nlist = nlist[0]

        li = nlist.find('li')
        self.assertEquals(len(li),2)
        li1 = li[0]

        #print "li", li.asBytes()
        p = li1.find(silva.p)
        self.assertEquals(len(p),1)
        p = p[0]
        self.assertEquals(p.extract_text(), 'one')

        li2 = li[1]
        sublist = li2.find('list')
        self.assertEquals(len(sublist), 1)
        sublist = sublist[0]

        li = sublist.find('li')
        self.assertEquals(len(li), 1)
        li = li[0]

        self.assertEquals(li.extract_text(), 'nested item')





class RoundtripWithTidy(Base):
    """ Transform and validate with 'tidy' if available. Also do a roundtrip """
    def setUp(self):
        self.transformer = Transformer(source='eopro3_0.silva', target='eopro3_0.html')

    def _check_string(self, string):
        string_withdoc = """<silva_document id="test"><title>test title</title>
                            <doc>%s</doc></silva_document>""" % string

        htmlnode = self._check_doc(string_withdoc)
        self.assert_(len(htmlnode)==1)
        return htmlnode[0].content

    def _check_doc(self, string):
        htmlnode = self.transformer.to_target(string)
        html = htmlnode.asBytes()
        self._checkhtml(html)
        silvanode = self.transformer.to_source(html)
        orignode = self.transformer.source_parser.parse(string)
        silvanode = silvanode.compact()
        orignode = orignode.compact()
        try:
            self.assertEquals(silvanode, orignode)
        except:
            print 
            print "*"*70
            print orignode.asBytes()
            print "-"*70
            print html
            print "-"*70
            print silvanode.asBytes()
            print "*"*70
            raise
        return htmlnode
        
    def test_heading_and_p(self):
        simple = '''
        <silva_document id="test"><title>doc title</title>
        <doc>
           <heading type="normal">top title</heading>
           <p type="lead">lead paragraph</p>
           <heading type="sub">sub title</heading>
           <p type="normal">normal paragraph</p>
           <heading type="subsub">subsub title</heading>
        </doc>
        </silva_document>'''
        self._check_doc(simple)

    def test_heading_and_p_special_chars(self):
        simple = '''
        <silva_document id="test"><title>doc title</title>
        <doc>
           <heading type="normal">top title</heading>
           <p type="normal">&quot;&amp;&lt;&gt;&apos;</p>
        </doc>
        </silva_document>'''
        self._check_doc(simple)

    def test_dlist_produces_term_desc(self):
        simple = '''
           <dlist type="normal">
              <dt>term1</dt><dd>desc1</dd>
           </dlist>
           '''

        silvanode = self.parse_silvafrag(simple)
        htmlnode = silvanode.conv()

        ul = htmlnode.find_one('ul')
        self.assertEquals(ul.attrs.get('type'), 'none')

        li = ul.find_one('li')

        self.assertEquals(li.find_one('term').extract_text(),
                          'term1')
        self.assertEquals(li.find_one('desc').extract_text()
                          , 'desc1')

        self._check_string(simple)

    def test_nlist_simple(self):
        simple = '''
           <nlist type="disc">
               <li><p>one item</p>
                   <list type="square"><li>1</li><li>2</li></list>
               </li>
           </nlist>'''

        silvanode = self.parse_silvafrag(simple)
        htmlnode = silvanode.conv()
        list = htmlnode.find_one('ul')
        self._check_string(simple)

    def _check_list(self, source, target=None):
        stag, stype = source.split(':')
        doc = '''
        <silva_document id="test"><title>test title</title>
        <doc>
           <%(stag)s type="%(stype)s">
              <li>eins</li>
              <li>zwei</li>
              <li>drei</li>
           </%(stag)s>
        </doc>
        </silva_document>''' % locals()

        htmldoc = self._check_doc(doc)

        if target:
            dtag, dtype = target.split(':')
            ltag = htmldoc.find_one('html').find_one('body').find_one(dtag)
            self.assertEquals(ltag.attrs.get('type'), dtype)

    def test_list_disc(self):
        self._check_list('list:disc', 'ul:disc')

    def test_list_circle(self):
        self._check_list('list:circle', 'ul:circle')

    def test_list_square(self):
        self._check_list('list:square', 'ul:square')

    def test_list_a(self):
        self._check_list('list:a', 'ol:a')

    def test_list_i(self):
        self._check_list('list:i', 'ol:i')

    def test_list_1(self):
        self._check_list('list:1', 'ol:1')


    def _nlist(self, tagtype):
        tag, type = tagtype.split(':')
        return '''
        <silva_document id="test"><title>doc title</title>
        <doc>
           <%(tag)s type="%(type)s">
              <li><p>eins</p></li>
              <li><p>zwei</p></li>
              <li><p>drei</p>
                 <list type="disc">
                    <li>one</li>
                 </list>
              </li>
           </%(tag)s>
        </doc>
        </silva_document>''' % locals()

    def test_nlist_disc(self):
        self._check_doc(self._nlist('nlist:disc'))
    def test_nlist_circle(self):
        self._check_doc(self._nlist('nlist:circle'))
    def test_nlist_square(self):
        self._check_doc(self._nlist('nlist:square'))
    def test_nlist_a(self):
        self._check_doc(self._nlist('nlist:a'))
    def test_nlist_i(self):
        self._check_doc(self._nlist('nlist:i'))
    def test_nlist_1(self):
        self._check_doc(self._nlist('nlist:1'))
    def test_nlist_none(self):
        self._check_doc(self._nlist('nlist:none'))

    def test_nlist_detection(self):
        frag = '<ul type="none"><li><ul type="circle"><li>one</li></ul></li></ul>'
        htmlnode = self.parse_htmlfrag(frag)
        silvanode = htmlnode.conv()
        silvanode.find_one('nlist')

    def _check_modifier(self, htmltag, silvatag):
        """ check that given markups work """
        frag = '<p type="normal"><%(silvatag)s>text</%(silvatag)s></p>' % locals()

        htmlnode = self._check_string(frag)
        body = htmlnode.find_one('body')
        p = body.find_one('p')
        htmlmarkup = p.find_one(htmltag)
        self.assertEquals(htmlmarkup.extract_text(), 'text')

    def test_modifier_b(self):
        self._check_modifier('strong','strong')

    def test_modifier_em(self):
        self._check_modifier('em','em')

    def test_modifier_underline(self):
        self._check_modifier('u','underline')

    def test_modifier_sub(self):
        self._check_modifier('sub','sub')

    def test_modifier_super(self):
        self._check_modifier('sup','super')

    def _test_link_with_absolute_url(self):
        """ check that a link works """
        silvadoc = '''<silva_document id="test"><title>title</title>
                        <doc><p type="normal">
                             <link url="http://www.heise.de">linktext</link>
                             </p>
                        </doc>
                      </silva_document>''' 
        htmlnode = self._check_doc(silvadoc)
        body = htmlnode.find('body')[0]
        p = body.find('p')[0]
        a = p.find('a')
        self.assert_(len(a)==1)
        a = a[0]
        self.assert_(a.attrs.get('href')=='http://www.heise.de')
        self.assert_(a.content.asBytes()=='linktext')

    def _test_table1(self):
        tabledoc = '''<table columns="3">
                          <row>
                              <field><p>eins</p></field>
                              <field><p>zwei</p></field>
                              <field><p>drei</p></field>
                          </row>
                      </table>''' 
        tablenode = self._check_string(tabledoc)

    def _check_table(self, **kwargs):
        attrs = []
        for name, value in kwargs.items():
            if value is not None:
                attrs.append('%s="%s"' % (name, value))

        attrs = " ".join(attrs)

        tabledoc = '''<table %(attrs)s>
                          <row>
                              <field><p>eins</p></field>
                              <field><p>zwei</p></field>
                              <field><p>drei</p></field>
                          </row>
                      </table>'''  % locals()
        tablenode = self._check_string(tabledoc)
        return tablenode

    def _test_table_listing(self):
        self._check_table(columns="3", type='listing', column_info="L:1 L:1 L:1")

    def _test_table_grid(self):
        self._check_table(columns="3", type='grid', column_info="L:1 L:1 L:1")

    def _test_table_data_grid(self):
        self._check_table(columns="3", type='datagrid', column_info="L:1 L:1 L:1")

    def _test_image(self):
        silvadoc = '''<silva_document id="test"><title>title</title>
                        <doc><image path="path/file"/></doc>
                      </silva_document>'''
        htmlnode = self._check_doc(silvadoc)
        body = htmlnode.find('body')[0]
        img = body.find('img')
        self.assertEquals(len(img),1)
        img = img[0]
        self.assertEquals(img.attrs.get('src'), 'path/file/image')

    def _test_br(self):
        """ check that 'br' works """
        self._check_string('<p>before<br/>after</p>')

    def test_preformatted(self):
        """ check that 'pre' (preformatted text) works """
        silvadoc = '<pre>\n  &quot;&gt;&lt;dies\n</pre>'
        htmlfrag = self.parse_htmlfrag(silvadoc)
        pre = htmlfrag.find('pre')
        self.assert_(len(pre)==1)
        pre = pre[0]
        self.assert_(pre.content.asBytes()=='\n  &quot;&gt;&lt;dies\n')

        self.assert_(pre.compact()==pre)

    def _checkhtml(self, html):
        cmd = 'tidy -eq -utf8'
        try:
            import popen2
            stdout, stdin, stderr = popen2.popen3(cmd)
	    stdin.write(html)
	    stdin.close()
	    output = stderr.read()
	    stderr.close()
	    stdout.close()
        except IOError:
            #print "tidy doesn't seem to be available, skipping html-check"
            return

        for line in output.split('\n'):
            if line.startswith('line') and line.find('Error')!=-1:
                raise AssertionError, "to_xhtml produced html errors, this is what i got\n" + html

class RoundtripSpecials(unittest.TestCase):
    def setUp(self):
        self.transformer = Transformer(source='eopro2_11.silva', target='eopro2_11.html')

    def _test_font_mapped_modifier(self, tag, tagcolor):
        # superscript is not supported by EoPro, we have to trick
        doc = '<p type="normal">text<%(tag)s>2</%(tag)s> yes</p>' % locals()
        silva_p = self.transformer.source_parser.parse(doc)
        html_p = silva_p.conv()[0]
        html_font = html_p.find('font')
        self.assert_(len(html_font)==1)
        html_font = html_font[0]
        self.assert_(html_font.attrs.get('color')==tagcolor)

        silva_back = html_p.conv()
        self.assert_(len(silva_back)==1)
        silva_back = silva_back[0]
        silva_super = silva_back.find(tag)
        self.assert_(len(silva_super)==1)
        silva_super = silva_super[0]
        self.assert_(silva_super.content.asBytes()=='2')

    def _test_mixin_paragraphs(self):
        doc = '<li>bef<strong>bold</strong><heading>heading</heading><p>qweq</p></li>'
        li = self.transformer.source_parser.parse(doc)[0]
        self.assertEquals(li.name(),'li')
        #print "before mixin", li.asBytes()
        content = silva.mixin_paragraphs(li)
        p = content.find('p')
        #print "mixin", content.asBytes()
        self.assertEquals(len(p), 2)
        self.assertEquals(p[1].extract_text(),'qweq')

    def _test_modifier_superscript(self):
        self._test_font_mapped_modifier('super','aqua')

    def _test_modifier_subscript(self):
        self._test_font_mapped_modifier('sub','blue')


def equiv_node(node1, node2):
    assert(node1.nodeName==node2.nodeName)
    assert(node1.nodeValue==node2.nodeValue)
    attrs1 = node1.attributes
    attrs2 = node2.attributes

    assert_len(attrs1, attrs2)
    
    childs1 = node1.childNodes
    childs2 = node2.childNodes

    assert_len(childs1, childs2)

    for c1 in childs1:
        ok=0
        for c2 in childs2:
            try:
                equiv_node(c1,c2)
                ok=1
                break
            except AssertionError, error:
                continue

        if not ok:
            #print "problem with", c1, "on", node1,node2
            raise AssertionError

#
# invocation of test suite
#
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HTML2XML, 'test'))
    suite.addTest(unittest.makeSuite(RoundtripWithTidy, 'test'))
    #suite.addTest(unittest.makeSuite(RoundtripSpecials, 'test'))
    return suite
    
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
