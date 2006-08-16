# Copyright (c) 2002-2006 Infrae. All rights reserved.
# See also LICENSE.txt

"""
Thank you Samuel, for having the brilliant idea!
"""

from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringValidator
from Products.Formulator.Widget import render_element,TextWidget
from Products.Silva.adapters.path import getPathAdapter

class LookupWindowValidator(StringValidator):
    
    def validate(self, field, key, REQUEST):
        # XXX no real validation at the moment
        return StringValidator.validate(self, field, key, REQUEST)

class ReferenceLookupWindowValidator(StringValidator):
    def validate(self, field, key, REQUEST):
        pad = getPathAdapter(REQUEST)
        value = StringValidator.validate(self, field, key, REQUEST)
        return pad.urlToPath(value)
    
class LookupWindowWidget(TextWidget):
    
    property_names = TextWidget.property_names  + ['onclick']
    
    default_onclick_handler = """reference.getReference(
    function(path, id, title) {
        document.getElementsByName('%(field_id)s')[0].value = path;;
        }, '%(url)s', '', true)
        """
    
    onclick = fields.TextAreaField(
        'onclick', 
        title='Onclick', 
        description='onclick handler implementation',
        default=default_onclick_handler,
        required=0,
        width='20', 
        height='3')
    
    def render(self, field, key, value, request):
        widget = []
        widget.append(
            render_element(
                'input', 
                type='button', 
                name=key + '_button', 
                css_class='transport',
                value='get reference...',
                extra='onclick="%s"' % self._onclick_handler(field, key)))
        widget.append(
            render_element(
                'input', 
                type='text', 
                name=key, 
                css_class=field.get_value('css_class'),
                value=value,
                size=field.get_value('display_width'), 
                maxlength=field.get_value('display_maxwidth'),
                extra=field.get_value('extra')))
        return ' '.join(widget)
    
    def _onclick_handler(self, field, key):
        request = getattr(field, 'REQUEST', None)
        if request is None:
            # XXX not sure yet
            return ''
        model = getattr(request, 'model', None)
        if model is None:
            # XXX not sure yet either
            return ''
        # when inside Kupu, 'model' points to the ExternalSource, which is not
        # very useful... however, in that case a request variable 'docref' will
        # be available to refer to the original model...
        if request.has_key('docref'):
            # we're in an ExternalSource, use the document in which it is
            # placed instead of the source as the model
            model = model.resolve_ref(request['docref'])
        container = model.get_container()
        interpolate = {
            'url': container.absolute_url(),
            'field_id': key}
        return field.get_value('onclick') % interpolate
    
class ReferenceLookupWindowWidget(LookupWindowWidget):
    def render(self, field, key, value, request):
        widget = []
        widget.append(
            render_element(
                'input', 
                type='button', 
                name=key + '_button', 
                css_class='transport',
                value='get reference...',
                extra='onclick="%s"' % self._onclick_handler(field, key)))
        widget.append(
            render_element(
                'input', 
                type='text', 
                name=key, 
                css_class=field.get_value('css_class'),
                value=getPathAdapter(field.REQUEST).pathToUrlPath(value),
                size=field.get_value('display_width'), 
                maxlength=field.get_value('display_maxwidth'),
                extra=field.get_value('extra')))
        return ' '.join(widget)
    
class LookupWindowField(StringField):
   
    meta_type = 'LookupWindowField'
    validator = LookupWindowValidator()
    widget = LookupWindowWidget()

class ReferenceLookupWindowField(StringField):

    meta_type = 'ReferenceLookupWindowField'
    validator = ReferenceLookupWindowValidator()
    widget = ReferenceLookupWindowWidget()
    
FieldRegistry.registerField(LookupWindowField)
FieldRegistry.registerField(ReferenceLookupWindowField)