"""
module for conversion from current silva xml (0.9.2) to
RealObjects EOPRO-3.0 XHTML.

the notation used for the transformation roughly
follows the ideas used with XIST (but simpler).  
Note that we can't use XIST itself as long as 
silva is running on a Zope version that 
doesn't allow python2.2.1

"""

__author__='holger krekel <hpk@trillke.net>'
__version__='$Revision: 1.4 $'

try:
    from transform.base import Element, Frag, Text
except ImportError:
    from Products.Silva.transform.base import Element, Frag, Text

import html

_attr_origin=u'silva_origin'
_attr_prefix=u'silva_'

# special attribute used for heuristics when transforming
# back to silva-xml

class SilvaElement(Element):
    def backattr(self):
        """ return dictionary with back attributes
            these attributes are later used for 
            the transformation from html to silvaxml.
        """
        attrs = {}
        for name, value in self.attrs.items():
            name = u'silva_'+name
            attrs[name]=value

        attrs[u'silva_origin']=self.name()
        return attrs

    def convert(self, context):
        """ for transformation of silva nodes to 
            html often we just want the content of 
            the node without the surrounding tags. 
        """
        return self.content.convert(context)

# -------------------------------------------------
# SILVA-XML Version 1 conversions to html
# -------------------------------------------------

class silva_document(SilvaElement):
    def convert(self, context):
        node_title = self.find_one('title')
        node_doc = self.find_one('doc')

        return html.html(
            html.head(
                html.title(self.attrs._id),
                html.meta(name='title', content=node_title.extract_text()),
                html.meta(name='id', content=self.attrs._id)
            ),
            html.body(
                html.doctitle(node_title.extract_text()),
                node_doc.convert(context),
            )
        )

class title(SilvaElement): 
    """ us used with documents """

class doc(SilvaElement):
    """ subtag of silva_document """

class heading(SilvaElement):
    def convert(self, context):
        level = self.attrs['type']
        h_tag = {u'normal' : html.h3, 
                 u'sub': html.h4, 
                 u'subsub': html.h5,
                 u'paragraph': html.h6,
                 u'subparagraph': html.p,
                 }.get(level, html.h3)

        return h_tag(
            self.content.convert(context),
            )

class p(SilvaElement):
    def convert(self, context):
        return html.p(
            self.content.convert(context),
            silva_type=self.attrs.get('type')
            )

class br(Element):
    def convert(self, context):
        return html.br()

class dlist(SilvaElement):
    """ Simple lists """

    def convert(self, context):
        #print "checking", self.asBytes()
        type = self.attrs.get('type')
        listtype = {'compact': 'circle'}.get(
            type,'none')

        li_list = []
        for tag,nexttag in zip(self.content, self.content[1:]):
            if tag.name()=='dt' and nexttag.name()=='dd':
                li_list.append(
                    html.li(
                        tag.convert(context), 
                        nexttag.convert(context)
                    )
                )
        return html.ul(
                       li_list,
                       type=listtype,
                       )

class dt(SilvaElement):
    """dlist define term"""
    def convert(self, context):
        return html.term(self.content.convert(context))

class dd(SilvaElement):
    """dlist define term"""
    def convert(self, context):
        return html.desc(self.content.convert(context))

class list(SilvaElement):
    """ Simple lists """
    def convert(self, context):
        listtype = self.attrs.get('type')
        listtype = listtype and listtype.lower() or u'none'

        attrs = {}
        if listtype in ['1','i','a']:
            tag = html.ol
            attrs[u'type']=listtype
        elif listtype in (u'disc',u'square',u'circle'):
            tag = html.ul
            attrs[u'type']=listtype
        else:
            tag = html.ul
            attrs[u'type']='none'

        return Frag(
            tag(
                self.find().compact().convert(context),
                attrs,
                )
            )

class nlist(list):
    pass

class li(SilvaElement):
    """ list items """
    def convert(self, context):
        return html.li(
            self.content.convert(context)
            )

class strong(SilvaElement):
    def convert(self, context):
        return html.strong(
            self.content.convert(context)
            )


class em(SilvaElement):
    def convert(self, context):
        return html.em(
            self.content.convert(context)
            )

class super(SilvaElement):
    def convert(self, context):
        return html.sup(self.content.convert(context))

    #
    #    return html.font(
    #       self.content.convert(context),
    #        color='aqua'
    #        )

class sub(SilvaElement):
    def convert(self, context):
        return html.sub(self.content.convert(context))

    #    return html.font(
    #        self.content.convert(context),
    #        color='blue'
    #        )

class underline(SilvaElement):
    def convert(self, context):
        return html.span(
            self.content.convert(context),
            style="text-decoration:underline;"
            )

class link(SilvaElement):
    def convert(self, context):
        return html.a(
            self.content.convert(context),
            href=self.attrs['url']
        )

class image(SilvaElement):
    def convert(self, context):
        src = self.attrs['path']
        try:
            src = src.content
        except AttributeError:
            pass
        align = self.attrs.get('alignment')
     
        return html.img(
            self.content.convert(context),
            src=src+'/image',
            link=self.attrs.get('link'),
            align=align
            )

class pre(SilvaElement):
    def compact(self):
        return self

    def convert(self, context):
        return html.pre(
            self.content.convert(context),
        )

class table(SilvaElement):
    def convert(self, context):
        #context['table']=self
        t = html.table(
            self.content.convert(context),
            self.backattr(),
            cols=self.attrs.get('columns'),
            #border=self.attrs.get('type') != 'plain' and '1' or None
            )
        #del context['table']
        return t
   
class row(SilvaElement):
    def convert(self, context):
        return html.tr(
            self.content.convert(context),
            #colspan = context['table'].attrs.get('columns')
        )
  
class field(SilvaElement):
    def convert(self, context):
        return html.td(
            self.content.convert(context)
        )


def mixin_paragraphs(container):
    """ wrap silva.p node around text"""
    content = Frag()
    breaks = 'heading','p','list','dlist','nlist','table'

    pre, tag, post = container.find_and_partition(breaks)
    if pre:
        content.append(p(*pre))
    if tag:
        content.append(tag)
    if post:
        content.extend(mixin_paragraphs(post))
    return content

""" current mapping of silva
h1  :  not in use, reserved for (future) Silva publication
       sections and custom templates
doctitle  :  title
h3  :  heading
h4  :  subhead
h5  :  subsubhead
"""
