#! /usr/bin/python
#
# Prettyprinter for ZopePagetemplates
# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# Author: Jan-Wijbrand Kolman (jw@infrae.com)
# $Revision: 1.5 $
#
# Issues:
#  * Testing, testing, testing. It would be rather horrible to 
#    loose characters here or there...
#  * This prettyprinter is SAX based. It might be that a DOM 
#    approach would have been simpler. However, I started this 
#    way and I wanted to see it through. The actual printing part
#    would not have been that different I guess.
#  * The code still contains string concatenations with a '+'. 
#    Some people regard this as ugly or un-pythonic. During
#    developing I found it more readable.
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
XHTML_DECLARATION = \
'''<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''
INDENTDEPTH = 2
INDENTCHAR = ' '
NEWLINE = '\n'
NEWLINE_SURROUNDED_ELEMENTS = [
    'table', 
    'tal:block',
    'form',
    ]
NO_INDENT_ON = [
    'head',
    'body',
    ]
FIRST_ATTR_ON_NEWLINE = 0
CLOSE_ELEMENT_ON_NEWLINE = 1
PUT_CLASS_ATTR_ON_TOP = 1
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
# extend list to contain both namespaced and
# non-namespaced TAL attributes
TAL_ORDER += ['tal:%s' % item for item in TAL_ORDER]


class PrettyZPT(saxutils.DefaultHandler):
    """
    """
    def __init__(self, writer=None):
        if not writer:
            self._write = write
        self._write(XHTML_DECLARATION + NEWLINE)

    ######################
    # SAX event handlers #
    def startDocument(self):
        self._data = []
        self._indent_level = -1

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
        #collect data within this element
        element = self._data[-1]
        element['data'] = element['data'] + ch
        element['textnodes'] += 1
        if element['textnodes'] == 1 and not element['childs']:
            self.printEndingStartElement(element['name'], element['attrs'])        

    #def resolveEntity(self, publicId, systemId):
    #    self._write('resolve: %s %s' % (publicId, systemId))
    #    return systemId
    
    def comment(self, content):
        self.printComment(content)

        
    ####################
    # Printing methods #
    def printCharacters(self, name, ch):
        ch = ' '.join(ch.strip().split())
        if ch:
            self._write(NEWLINE + self._indent() + (INDENTCHAR * INDENTDEPTH) + ch)

    def printStartingStartElement(self, name, attrs):
        if name in NEWLINE_SURROUNDED_ELEMENTS:
            self._write(NEWLINE)
        self._write(NEWLINE + self._indent() + '<%s' % name)
        self.printAttributes(name, attrs)

    def printEndingStartElement(self, name, attrs):
        if attrs.getLength() > 1:
            if CLOSE_ELEMENT_ON_NEWLINE:
                self._write(NEWLINE)
                self._write(self._indent())
        self._write('>')

    def printEndElement(self, name, attrs, childs, txtnodes):
        if childs or txtnodes:
            self._write(NEWLINE + self._indent() + '</%s>' % name)
        else:                                
            if attrs.getLength() > 1 and CLOSE_ELEMENT_ON_NEWLINE:
                self._write(NEWLINE)
                self._write(self._indent())
            else:
                self._write(' ') # e.g. for <br />
            self._write('/>')
        if name in NEWLINE_SURROUNDED_ELEMENTS:
            self._write(NEWLINE)

    def printAttributes(self, name, attrs):
        if attrs.getLength() == 1:
            key = attrs.keys()[0]
            value = attrs.values()[0]
            self._write(' %s="%s"' % (key, self._attributeValues(value)))
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
            
            indent = self._indent() + (INDENTCHAR * INDENTDEPTH)
            if FIRST_ATTR_ON_NEWLINE:
                self._write(NEWLINE)
            else:
                key = keys[0]
                value = self._attributeValues(attrs[key])
                self._write(' %s="%s"' % (key, value))
                keys = keys[1:]

            for key in keys:
                value = self._attributeValues(attrs[key])
                self._write(NEWLINE + indent + '%s="%s"' % (key, value))

    def printComment(self, content):
        self._write(NEWLINE + self._indent() + '<!-- ' + content + ' -->' + NEWLINE)

    def _attributeValues(self, value):
        multi_indent = self._indent() + (INDENTCHAR * INDENTDEPTH) * 2
        # split on ';' (in case of e.g. tal:define and tal:attributes), and
        # strip whitespace from each element
        # FIXME: what about javascript?
        values = map(lambda s: s.strip(), value.split(';'))
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
                    lines.append(NEWLINE + multi_indent + value + ';')
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
    parser = make_parser()
    handler = PrettyZPT()
    parser.setContentHandler(handler)
    parser.setEntityResolver(handler)

    lh = saxlib.LexicalHandler()    
    #Trick to get comment "events" handled by the PrettyZPT handler
    lh.comment = handler.comment
    parser.setProperty(saxlib.property_lexical_handler, lh)

    #Replace to not get the entities parsed
    xml = StringIO(sys.stdin.read().replace('&', '&amp;'))
    parser.parse(xml)

if __name__ == '__main__':
    usage = """
This pretty printer uses stdin for ZPT input and stdout for
pretty printed result.
"""
    if '--help' in sys.argv[1:]:
        print usage
        sys.exit(0)
    opts, files = getopt(sys.argv[1:], 'p:', ['placeholderoption='])
    main(opts, files)
    sys.exit(0)


