#! /usr/bin/python
#
# Prettyprinter for ZopePagetemplates
# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# Author: Jan-Wijbrand Kolman (jw@infrae.com)
# $Revision: 1.9 $
#
# Issues:
#  * Testing, testing, testing. It would be rather horrible to 
#    loose characters here or there...
#  * This prettyprinter is SAX based. It might be that a DOM 
#    approach would have been simpler. However, I started this 
#    way and I wanted to see it through. The actual printing part
#    would not have been that different I guess.
#  * Would a namespace aware parser make things easier?
#  * Making better use of existing methods and classes in the 
#    XML libs.
#  * NEWLINE on different OS's
#  * Javascript in TALES: escape the ';'"
#  * The '&' in entities are escapes now, to get the entity in unparsed
#    shape back in the resulting xhtml - is there a better way?
#
# ToDos:
#  * More testing
#  * More config options
#  * Refactor for reusability e.g. for Zope3 zcml files
#  * Limit line widths.
#  * Better command line interface (e.g. overriding config options)
#

import sys
from getopt import getopt
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from xml.sax import make_parser
from xml.sax import saxutils
from xml.sax import saxlib


### Configurable options: ###
WRITE_XML_DECL = 1
WRITE_XHTML_DECL = 1
XML_DECLARATION = \
'''<?xml version="1.0"?>'''
XHTML_DECLARATION = \
'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''
INDENTDEPTH = 2
INDENTCHAR = ' '
NEWLINE = '\n'
NEWLINE_SURROUNDED_ELEMENTS = [
    'table', 
    'tal:block',
    'form',
    ]
NO_INDENT_ON = [
    'html',
    'head',
    'body',
    ]
DONT_TOUCH_TXTNODE_FOR = [
    'script',
    'style',
    ]
FIRST_ATTR_ON_NEWLINE = 0
CLOSE_ELEMENT_ON_NEWLINE = 0
PUT_CLASS_ATTR_ON_TOP = 1
SPLIT_ATTR_VALUES_FOR = [
    'define',
    'attributes',
    ]
TAL_ORDER = [
    'define',
    'condition',
    'repeat',
    'content',
    'replace',
    'attributes',
    'omit-tag',
    ]

### Tricks ###
# extend lists to contain both namespaced and
# non-namespaced TALs
TAL_ORDER += ['tal:%s' % item for item in TAL_ORDER]
SPLIT_ATTR_VALUES_FOR += ['tal:%s' % item for item in TAL_ORDER]


class PrettyZPT(saxutils.DefaultHandler):
    """
    """
    def __init__(self, options, writer=None):
        self._data = []
        self._indent_level = -1
        if not writer:
            self._write = write

        self.WRITE_XML_DECL = WRITE_XML_DECL
        if options.has_key('--no-xml-decl'):
            self.WRITE_XML_DECL = 0

        self.WRITE_XHTML_DECL = WRITE_XHTML_DECL
        if options.has_key('--no-xhtml-decl'):
            self.WRITE_XHTML_DECL = 0

        self.NEWLINE_SURROUNDED_ELEMENTS  = NEWLINE_SURROUNDED_ELEMENTS
        if options.has_key('--no-surrounding-newlines'):
            self.NEWLINE_SURROUNDED_ELEMENTS = []

    ######################
    # SAX event handlers #
    def startDocument(self):
        self._data = []
        self._indent_level = -1
        if self.WRITE_XML_DECL:
            self._write('%s%s' % (XML_DECLARATION, NEWLINE))
        if self.WRITE_XHTML_DECL:
            self._write('%s%s' % (XHTML_DECLARATION, NEWLINE))

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if self._data:
            element = self._data[-1] 
            element['childs'] += 1
            if element['childs'] == 1 and not element['textnodes']:
                self.printEndingStartElement(element['name'], element['attrs'])
            if element['data']:
                self.printCharacters(element['name'], element['data'])
                element['data'] = ''

        if not name in NO_INDENT_ON:
            self._indent_level += 1
        self.printStartingStartElement(name, attrs)
        self.printAttributes(name, attrs)
        #append to data stack
        self._data.append(
            {'name':name, 'attrs':attrs, 'data':'', 'childs':0, 'textnodes':0})

    def endElement(self, name):
        #pop from stack
        element = self._data.pop()
        if element['data']:
            self.printCharacters(element['name'], element['data'])
        self.printEndElement(name, element['attrs'], element['childs'], element['textnodes'])
        if not name in NO_INDENT_ON:
            self._indent_level -= 1

    def characters(self, ch):
        if not self._data:
            return
        #collect data within this element
        element = self._data[-1]
        element['data'] += ch
        element['textnodes'] += 1
        if element['textnodes'] == 1 and not element['childs']:
            self.printEndingStartElement(element['name'], element['attrs'])        

    def comment(self, content):
        if self._data:
            element = self._data[-1]
            if not element['textnodes'] and not element['childs']:
                self.printEndingStartElement(element['name'], element['attrs'])
        self.printComment(content)

    def skippedEntity(self, entity): 
        pass
	
    def startEntity(self, name):
        pass

    def resolveEntity(self, pubId, sysId):	
	return StringIO()

    ####################
    # Printing methods #
    def printCharacters(self, name, ch):
        if name in DONT_TOUCH_TXTNODE_FOR:
            self._write('%s%s' % (NEWLINE, ch.strip()))
        else:
            ch = ' '.join(ch.strip().split())
            if ch: self._write("%s%s%s%s" % (
                NEWLINE, self._indent(), (INDENTCHAR * INDENTDEPTH), ch))

    def printStartingStartElement(self, name, attrs):
        if name in self.NEWLINE_SURROUNDED_ELEMENTS:
            self._write(NEWLINE)
        if self._data:
            self._write(NEWLINE) # so, not for start of document. A bit ugly.
        self._write('%s<%s' % (self._indent(), name))

    def printEndingStartElement(self, name, attrs):
        if attrs.getLength() > 1:
            if CLOSE_ELEMENT_ON_NEWLINE:
                self._write(NEWLINE)
                self._write(self._indent())
        self._write('>')

    def printEndElement(self, name, attrs, childs, txtnodes):
        if childs or txtnodes:
            self._write('%s%s</%s>' % (NEWLINE, self._indent(), name))
        else:                                
            if attrs.getLength() > 1 and CLOSE_ELEMENT_ON_NEWLINE:
                self._write(NEWLINE)
                self._write(self._indent())
            else:
                self._write(' ') # e.g. for <br />
            self._write('/>')
        if name in self.NEWLINE_SURROUNDED_ELEMENTS:
            self._write(NEWLINE)

    def printAttributes(self, name, attrs):
        if attrs.getLength() == 1:
            key = attrs.keys()[0]
            value = attrs.values()[0]
            self._write(' %s="%s"' % (key, self._attributeValues(name, attrs, key)))
        elif attrs.getLength() > 1:
            html_keys = []
            tal_keys = []
            metal_keys = []

            if name.startswith('tal:'):
                #Element in TAL NS
                tal_keys, unused, metal_keys = self._attributesHelper(attrs.keys())
            elif name.startswith('metal:'):
                #Element in METAL NS
                metal_keys, tal_keys, unused = self._attributesHelper(attrs.keys())
            else:
                html_keys, tal_keys, metal_keys = self._attributesHelper(attrs.keys())
                
            tal_keys.sort(self._sortTAL)
            html_keys.sort(self._sortHTML)
            keys = html_keys + tal_keys + metal_keys
            
            indent = '%s%s' % (self._indent(), (INDENTCHAR * INDENTDEPTH))
            if FIRST_ATTR_ON_NEWLINE:
                self._write(NEWLINE)
            else:
                key = keys[0]
                value = self._attributeValues(name, attrs, key)
                self._write(' %s="%s"' % (key, value))
                keys = keys[1:]

            for key in keys:
                value = self._attributeValues(name, attrs, key)
                self._write('%s%s%s="%s"' % (NEWLINE, indent, key, value))

    def printComment(self, content):
        self._write('%s%s<!-- %s -->' % (NEWLINE, self._indent(), content.strip()))

    def printEntity(self, entity):
        pass # sys.stdout.write("bla bla bla %s" % (entity))

    def _attributeValues(self, name, attrs, key):        
        attr = key
        value = attrs[key]
        multi_indent = '%s%s' % (self._indent(), (INDENTCHAR * INDENTDEPTH) * 2)
        if attr in SPLIT_ATTR_VALUES_FOR:
            # split on ';' (in case of e.g. tal:define and tal:attributes), and
            # strip whitespace from each element
            # FIXME: What about javascript? 
            #        What about tal:define="string:&nbps;;"?
            values = map(lambda s: s.strip(), value.split(';'))
        else:
            values = [value,]
        # split on whitespace, and join again with one space. This gets rid 
        # of newlines and manual indentation
        values = map(lambda s: ' '.join(s.split()) , values)

        if len(values) == 1:
            return values[0]
        else:
            # begin values on newline, indent even more
            lines = []
            for value in values:
                if value:
                    lines.append('%s%s%s;' % (NEWLINE, multi_indent, value))
            #if attrs.getLength() == 1 and CLOSE_ELEMENT_ON_NEWLINE:
            #    # In case of multiple subvalues, in one attribute, the closing
            #    # bracket should go on a new line.
            #    lines.append(NEWLINE + self._indent())
            return ''.join(lines)

    def _attributesHelper(self, attrs):
        nonNS_keys = []
        tal_keys = []
        metal_keys = []
        #split
        for attr in attrs:
            if attr.startswith('tal:'):
                tal_keys.append(attr)
            elif attr.startswith('metal:'):
                metal_keys.append(attr)
            else:
                nonNS_keys.append(attr)        
        return nonNS_keys, tal_keys, metal_keys

    def _indent(self):
        return INDENTCHAR * self._indent_level * INDENTDEPTH

    def _sortTAL(self, attr1, attr2):
        if TAL_ORDER.index(attr1) < TAL_ORDER.index(attr2):
            return -1
        return 1

    def _sortHTML(self, attr1, attr2):
        if PUT_CLASS_ATTR_ON_TOP:
            if attr1 == 'class':
                return -1
            if attr2 == 'class':
                return 1
        if attr1 < attr2:
            return -1
        return 1

#############
# Main app. #
def write(ch):
    sys.stdout.write(ch)

def main(options, files):
    parser = make_parser() # ['xml.sax.drivers2.drv_sgmlop', 'xml.sax.drivers2.drv_pyexpat', 'xml.sax.drivers2.drv_xmlproc', ])
    #sys.stderr.write(str(parser) + '\n\n\n')

    handler = PrettyZPT(options, writer=None)
    parser.setContentHandler(handler)
    parser.setEntityResolver(handler)

    lh = saxlib.LexicalHandler()    
    #Trick to get comment "events" handled by the PrettyZPT handler
    lh.comment = handler.comment
    #lh.startEntity = handler.startEntity
    parser.setProperty(saxlib.property_lexical_handler, lh)

    #Replace to get the entities unparsed
    xml = StringIO(sys.stdin.read().replace('&', '&amp;'))
    parser.parse(xml)

if __name__ == '__main__':
    usage = """
This pretty printer uses stdin for ZPT input and stdout for
pretty printed result.

Options:
  --help:           this help summary
  --no-xml-decl:    do not write XML declaration
  --no-xhtml-decl:  do not write XHTML declaration
"""
    if '--help' in sys.argv[1:]:
        print usage
        sys.exit(0)
    opts, files = getopt(
        sys.argv[1:], 'p:', [
        'no-xml-decl',
        'no-xhtml-decl',
        'no-surrounding-newlines',
        ])    
    options = {}
    for key,value in opts:
        options[key] = value
    main(options, files)
    sys.exit(0)


