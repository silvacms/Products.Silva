from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
import SilvaPermissions
import ForgivingParser
from cgi import escape

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
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                result.append(escape(child.data, 1))
                continue
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.nodeName == 'strong':
                result.append('<strong>')
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</strong>')
            elif child.nodeName == 'em':
                result.append('<em>')
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</em>')
            elif child.nodeName == 'link':
                result.append('<a href="%s">' %
                              escape(child.getAttribute('url'), 1))
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</a>')
            elif child.nodeName == 'underline':
                result.append('<u>')
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                    result.append('</u>')
            elif child.nodeName == 'index':
                result.append('<a name="%s">' %
                              escape(child.getAttribute('name'), 1))
                for subchild in child.childNodes:
                    result.append(escape(subchild.data, 1))
                result.append('</a>')
            #elif child.nodeName == 'person':
            #    for subchild in child.childNodes:
            #        result.append(escape(subchild.data, 1))
            else:
                raise EditorSupportError, "Unknown element: %s" % child.nodeName
        return self.normalize(''.join(result))

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
            
        return self.normalize(''.join(result))
    
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

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'replace_text')
    def replace_text(self, node, text):
        """Replace text in a text containing node.
        """
        # first preprocess the text, collapsing all whitespace
        text = self.normalize(text)
        
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

    def normalize(self, s):
        return ' '.join(s.split())
    
InitializeClass(EditorSupport)
