# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from types import UnicodeType

from DocumentTemplate.DT_Util import html_quote
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringValidator
from Products.Formulator.Widget import render_element,Widget

# For XML-Conversions for editors
from Products.SilvaDocument.transform.Transformer import EditorTransformer
from Products.SilvaDocument.transform.base import Context

class KupuPopupValidator(StringValidator):
    def validate(self, field, key, REQUEST):
        # XXX no validation at the moment, but perhaps
        #we'd want to validate to an xhtml standard,
        # or validate, even remove invalid tags (e.g. tables)
        val = StringValidator.validate(self, field, key, REQUEST)
        val = "<div>%s</div>"%val
        transformer = EditorTransformer(editor='kupu')

        browser = 'Mozilla'
        if REQUEST['HTTP_USER_AGENT'].find('MSIE') > -1:
            browser = 'IE'
        ctx = Context(browser=browser,
                      request=REQUEST)
        #replace any &nbsp; with \xa0, as xml.dom.minidom (used by to_source)
        # can't handle named character entities.  Normal kupu usage should not
        # introduce &nbsp;, but perhaps through copy/pasting they may be
        # present.
        if isinstance(val,UnicodeType):
            val = val.replace(u'&nbsp;', u'\xa0')
        else:
            val = val.replace('&nbsp;', '\xc2\xa0')

        nodes = transformer.to_source(targetobj=val, context=ctx)
        content = nodes.asBytes(encoding="UTF8")

        renderer = field.service_renderer_registry.getRenderer('Silva Document', 'Basic XSLT Renderer')
        content = '<doc xmlns="http://infrae.com/ns/silva_document">%s</doc>'%content
        content = renderer.render_snippet(content)
        return content
    
class KupuPopupWidget(Widget):
    property_names = Widget.property_names + ['textstyles','buttons','toolboxes']

    textstyles = fields.MultiListField('textstyles',
                                       title="Text Styles",
                                       description=(
                                           "The text styles selected will be "
                                           "visible within the kupu popup."),
                                       default=['P|normal','P|lead','P|annotation'],
                                       items=(('plain','P|normal'),
                                              ('lead','P|lead'),
                                              ('annotation','P|annotation'),
                                              ('title','H2'),
                                              ('heading','H3'),
                                              ('sub','H4'),
                                              ('subsub','H5'),
                                              ('paragraph','H6'),
                                              ('subparagraph','H6|sub'),
                                              ('preformatted','PRE'),
                                              )
                                       )
    buttons = fields.MultiListField('buttons',
                                    title='Buttons',
                                    description=(
                                        'The buttons selected will be visible ',
                                        'within the kupu popup'),
                                    default=['kupu-save-button','kupu-bold-button','kupu-italic-button','kupu-underline-button'],
                                    items=(('save','kupu-save-button'),
                                           ('bold','kupu-bold-button'),
                                           ('italic','kupu-italic-button'),
                                           ('underline','kupu-underline-button'),
                                           ('sub','kupu-subscript-button'),
                                           ('sup','kupu-superscript-button'),
                                           ('ol','kupu-list-ol-addbutton'),
                                           ('ul','kupu-list-ul-addbutton'),
                                           ('dl','kupu-list-dl-addbutton'),
                                           ('source','kupu-source-button'))
                                    )
    toolboxes = fields.MultiListField('toolboxes',
                                      title='Toolboxes',
                                      description=(
                                          'The toolbox names selected here '
                                          'will be visible in the popup kupu'),
                                      default=['kupu-toolbox-links',
                                               'kupu-toolbox-indexes',
                                               'kupu-toolbox-abbr',
                                               'kupu-toolbox-cleanupexpressions',
                                               'kupu-toolbox-typochars',
                                               'kupu-toolbox-save'],
                                      items=(('link','kupu-toolbox-links'),
                                             ('anchor/index','kupu-toolbox-indexes'),
                                             ('image','kupu-toolbox-images'),
                                             ('abbr/acronym','kupu-toolbox-abbr'),
                                             ('cleanup','kupu-toolbox-cleanupexpressions'),
                                             ('external source','kupu-toolbox-extsource'),
                                             ('table','kupu-toolbox-tables'),
                                             ('typographical','kupu-toolbox-typochars'),
                                             ('save','kupu-toolbox-save')
                                             )
                                      )

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default html in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    def render(self, field, key, value, REQUEST):
        
        #NOTE: self.buttons is still a DummyField
        enabled_buttons = [ f.encode('ascii') for f in field.values['buttons'] ]
        neg_buttons = [ i[1].encode('ascii') for i in self.buttons.get_real_field().get_value('items') if i[1] not in enabled_buttons ]
        #NOTE: self.textstyles is still a DummyField
        enabled_styles = [ f.encode('ascii') for f in field.values['textstyles'] ]
        neg_styles = [ i[1].encode('ascii') for i in self.textstyles.get_real_field().get_value('items') if i[1] not in enabled_styles ]
        #NOTE: self.toolboxes is still a DummyField
        enabled_tools = [ f.encode('ascii') for f in field.values['toolboxes'] ]
        neg_tools = [ i[1].encode('ascii') for i in self.toolboxes.get_real_field().get_value('items') if i[1] not in enabled_tools ]
        val = render_element("input",
                             css_class="kupupopupeditbutton button transporter",
                             type="button",
                             value="edit...",
                             onclick="openPopupKupu('%s',%s,%s,%s)"%(key,
                                                                     str(neg_buttons),
                                                                     str(neg_styles),
                                                                     str(neg_tools)),
                             id=key + "editcontent")
        val += render_element("div",
                             id=key + "content",
                             css_class="kupupopupcontentbox",
                             contents=value or '&nbsp;'
                             )
        val += render_element("textarea",
                              name=key,
                              id=key,
                              css_class=field.get_value('css_class') + " kupupopuptextarea",
                              rows="2",
                              contents=html_quote(value),
                              height="1")
        return val
    def render_view(self, field, value):
        return value
                              
class KupuPopupField(StringField):
    meta_type = 'KupuPopupWindowField'
    validator = KupuPopupValidator()
    widget = KupuPopupWidget()
    
FieldRegistry.registerField(KupuPopupField)
