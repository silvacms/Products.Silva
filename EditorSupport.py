# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.19 $
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions
import ForgivingParser
import re

class EditorSupportError(Exception):
    pass

class EditorSupport:
    """XML editor support.
    """
    security = ClassSecurityInfo()

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_text_as_html')
    def render_text_as_html(self, node):
        """Render textual content as HTML.
        """
        result = []
        output_convert = self.output_convert_html
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(output_convert(child.data))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<strong>')
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                result.append('</strong>')
            elif child.nodeName == 'em':
                result.append('<em>')
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                result.append('</em>')
            elif child.nodeName == 'link':
                result.append('<a href="%s">' %
                              output_convert(child.getAttribute('url')))
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                    result.append('</u>')
            elif child.nodeName == 'index':
                result.append('<a class="index-element" name="%s">' %
                              output_convert(child.getAttribute('name')))
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                result.append('</a>')
            #elif child.nodeName == 'person':
            #    for subchild in child.childNodes:
            #        result.append(output_convert(subchild.data))
            else:
                raise EditorSupportError, "Unknown element: %s" % child.nodeName
        return ''.join(result)


    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_heading_as_html')
    def render_heading_as_html(self, node):
        """Render heading content as HTML.
        """
        result = []
        output_convert = self.output_convert_html
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(output_convert(child.data))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'index':
                result.append('<a class="index-element" name="%s">' %
                              output_convert(child.getAttribute('name')))
                for subchild in child.childNodes:
                    result.append(output_convert(subchild.data))
                result.append('</a>')
            else:
                raise EditorSupportError, "Unknown element: %s" % child.nodeName
        return ''.join(result)

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'render_text_as_editable')
    def render_text_as_editable(self, node):
        """Render textual content as editable text.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(child.data)
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('**')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('**')
            elif child.nodeName == 'em':
                result.append('++')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('++')
            elif child.nodeName == 'link':
                result.append('((')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('|')
                result.append(child.getAttribute('url'))
                result.append('))')
            elif child.nodeName == 'underline':
                result.append('__')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('__')
            elif child.nodeName == 'index':
                result.append('[[')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('|')
                result.append(child.getAttribute('name'))
                result.append(']]')
            #elif child.nodeName == 'person':
            #    result.append('{{')
            #    for subchild in child.childNodes:
            #        result.append(subchild.data)
            #    result.append('}}')
            else:
                raise EditorSupportError, "Unknown element: %s" % child.nodeName
        return self.output_convert_editable(''.join(result))

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'render_heading_as_editable')
    def render_heading_as_editable(self, node):
        """Render textual content as editable text.
        """
        result = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(child.data)
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'index':
                result.append('[[')
                for subchild in child.childNodes:
                    result.append(subchild.data)
                result.append('|')
                result.append(child.getAttribute('name'))
                result.append(']]')
            else:
                raise EditorSupportError, "Unknown element: %s" % child.nodeName
            
        return self.output_convert_editable(''.join(result))
    
    _strongStructure = ForgivingParser.Structure(['**', '**'])
    _emStructure = ForgivingParser.Structure(['++', '++'])
    _linkStructure = ForgivingParser.Structure(['((', '|', '))'])
    _underlineStructure = ForgivingParser.Structure(['__', '__'])
    _indexStructure = ForgivingParser.Structure(['[[', '|', ']]'])
    #_personStructure = ForgivingParser.Structure(['{{', '}}'])

    _parser = ForgivingParser.ForgivingParser([
        _strongStructure,
        _emStructure,
        _linkStructure,
        _underlineStructure,
        _indexStructure])

    _headingParser = ForgivingParser.ForgivingParser([
        _indexStructure])

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'replace_text')
    def replace_text(self, node, text):
        """Replace text in a text containing node.
        """
        # first preprocess the text, collapsing all whitespace
        # FIXME: does it make sense to expect cp437, which is
        # windows only?
        text = self.input_convert(text)

        # parse the data
        result = self._parser.parse(text)

        # get actual DOM node
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        # FIXME: hack to make copy of all childnodes
        children = [child for child in node.childNodes]
        children.reverse()
        for child in children:
            node.removeChild(child)

        # now use tokens in result to add them to XML
        for structure, data in result:
            if structure is None:
                # create a text node, data is plain text
                newnode = doc.createTextNode(data)
                node.appendChild(newnode)
            elif structure is self._strongStructure:
                newnode = doc.createElement('strong')
                newnode.appendChild(doc.createTextNode(data[0]))
                node.appendChild(newnode)
            elif structure is self._emStructure:
                newnode = doc.createElement('em')
                newnode.appendChild(doc.createTextNode(data[0]))
                node.appendChild(newnode)
            elif structure is self._linkStructure:
                link_text, link_url = data
                newnode = doc.createElement('link')
                newnode.appendChild(doc.createTextNode(link_text))
                newnode.setAttribute('url', link_url)
                node.appendChild(newnode)
            elif structure is self._underlineStructure:
                newnode = doc.createElement('underline')
                newnode.appendChild(doc.createTextNode(data[0]))
                node.appendChild(newnode)
            elif structure is self._indexStructure:
                index_text, index_name = data
                newnode = doc.createElement('index')
                newnode.appendChild(doc.createTextNode(index_text))
                newnode.setAttribute('name', index_name)
                node.appendChild(newnode)
            #elif structure is self._personStructure:
            #    newnode = doc.createElement('person')
            #    newnode.appendChild(doc.createTextNode(data[0]))
            #    node.appendChild(newnode)
            else:
                raise EditorSupportError, "Unknown structure: %s" % structure


    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'replace_heading')
    def replace_heading(self, node, text):
        """Replace text in a heading containing node.
        """
        # first preprocess the text, collapsing all whitespace
        # FIXME: does it make sense to expect cp437, which is
        # windows only?
        text = self.input_convert(text)

        # parse the data
        result = self._headingParser.parse(text)

        # get actual DOM node
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        # FIXME: hack to make copy of all childnodes
        children = [child for child in node.childNodes]
        children.reverse()
        for child in children:
            node.removeChild(child)

        # now use tokens in result to add them to XML
        for structure, data in result:
            if structure is None:
                # create a text node, data is plain text
                newnode = doc.createTextNode(data)
                node.appendChild(newnode)
            elif structure is self._indexStructure:
                index_text, index_name = data
                newnode = doc.createElement('index')
                newnode.appendChild(doc.createTextNode(index_text))
                newnode.setAttribute('name', index_name)
                node.appendChild(newnode)
            #elif structure is self._personStructure:
            #    newnode = doc.createElement('person')
            #    newnode.appendChild(doc.createTextNode(data[0]))
            #    node.appendChild(newnode)
            else:
                raise EditorSupportError, "Unknown structure: %s" % structure

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'replace_pre')
    def replace_pre(self, node, text):
        """Replace text in a pre containing node.
        """
        # first preprocess the text, collapsing all whitespace
        # FIXME: does it make sense to expect cp437, which is
        # windows only?
        text = self.input_convert2(text)

        # get actual DOM node
        node = node._node
        doc = node.ownerDocument

        # remove all old subnodes of node
        # FIXME: hack to make copy of all childnodes
        # XXX This now removes all subnodes, while this will only be 1 in practice
        children = [child for child in node.childNodes]
        children.reverse()
        for child in children:
            node.removeChild(child)

        if text.split():
            # If text contains more than just whitespace:
            newNode = doc.createTextNode(text)
            node.appendChild(newNode)

    # XXX should really be in a better place, like some kind of editor
    # support service
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'split_silva_html')
    def split_silva_html(self, html, min_characters):
        """Split html into two blocks. There'll be at least min_characters
        in the first block, and the rest will be in the second block.
        If the second block will be larger than the first, the html
        is split equally instead.
        """
        l = len(html)
        if l - min_characters < min_characters:
            i = _find_split_point(html, min_characters)
        else:
            i = _find_split_point(html, l/2)
        return html[:i], html[i:]

# do never split at a heading, so h2/h3 not included
tags = ['p', 'ol', 'ul', 'table']
split_pattern = re.compile("(%s)" % '|'.join(
    ['</%s>' % tag for tag in tags]))
def _find_split_point(html, approximate_point):
    r = split_pattern.search(html, approximate_point)
    if r is not None:
        return r.end()
    else:
        return len(html)

InitializeClass(EditorSupport)
