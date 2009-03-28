# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt

"""
Thank you Samuel, for having the brilliant idea!
"""

from urllib import quote
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringValidator
from Products.Formulator.Widget import render_element,TextWidget
from Products.Silva.adapters.path import getPathAdapter

from Products.Five import BrowserView
from urlparse import urlparse
from zExceptions import BadRequest

from silva.core.interfaces import ISilvaObject

class EditButtonRedirector(BrowserView):
    """This view is used by the ReferenceLookupWindow's 'edit reference'
       button to redirect to the reference object's edit screen.
       It will raise a BadRequest error if the reference/location has a
       scheme or netloc, if the location cannot be found, or if it is not
       a Silva Object.  
       
       The decision to not raise NotFounds is kind of due
       to security (e.g. using this redirector to fish for valid paths)
       And also because the 'loc' parameter is a requirement for this
       view, and if it is invalid, it is a bad request, not a not
       found or some other error."""

    def __call__(self,loc,checkonly='n'):
        request = self.request
        parts = urlparse(loc)
        if parts[0] != '' or parts[1] != '':
            raise BadRequest("Invalid location.  Unable to redirect to the edit view of absolute urls.")
        path = parts[2]
        if path.startswith('/'):
            #this will convert an absolute path without a netloc
            # to a zope path, taking into account virtualhosting
            path = request.physicalPathFromURL(path)
        #attempt to traverse to this object
        ob = self.context.restrictedTraverse(path,None)
        if not ob:
            raise BadRequest("Invalid location.  Unable to redirect to the edit view.")
        if ISilvaObject.providedBy(ob):
            if checkonly == 'y':
                return "valid"
            else:
                request.response.redirect(ob.absolute_url() + '/edit')
                return "redirecting"
        raise BadRequest("Invalid location.  Target must be a Silva Object in order to edit")

        
        

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
        }, '%(url)s', '', true, '%(selected_path)s')
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
                css_class='button transporter',
                style='margin-left:0',
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
        url = ''
        if request.has_key('docref'):
            # we're in an ExternalSource, use the document in which it is
            # placed instead of the source as the model
            url = model.resolve_ref(
                quote(request['docref'])).get_container().absolute_url()
        else:
            # start where we last looked something up
            url = request.SESSION.get('lastpath') or '' 
        if url == '':
            url = model.get_container().absolute_url()
        interpolate = {
            'url': url,
            'field_id': key,
            'selected_path': getattr(field ,'value', '')}
        return field.get_value('onclick') % interpolate
    
class ReferenceLookupWindowWidget(LookupWindowWidget):
    property_names = LookupWindowWidget.property_names  + ['button_label','show_edit_button']
    
    button_label = fields.StringField(
        'button_label',
        title='Label for get reference button',
        description='The label for the get reference button',
        default='get reference...',
        required=0)
    
    show_edit_button = fields.CheckBoxField(
        'show_edit_button', 
        title='Show Edit Reference Button', 
        description="Adds an 'Edit Reference' button to the widget.  When clicked, this will open a new window and redirect to the edit tab for the reference, if it is a valid Silva relative reference.  NOTE: only works in kupu.",
        required=0,
        default="")

    def render(self, field, key, value, request):
        widget = []
        widget.append('<table class="kupu-link-reference-table" cellpadding="0" cellspacing="0"><tr><td width="24">')
        widget.append(
            render_element(
                'button',
                name=key + '_button',
                css_class="kupu-button kupu-link-reference button transporter",
                title=field.get_value('button_label') or 'get reference...',
                onclick="%s;return false;" % self._onclick_handler(field, key),
                contents=render_element(
                    'img',
                    width='16',
                    height='16',
                    src='/silva/globals/system-search.png'
                    )
            )
        )
        widget.append('</td><td>')
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
        widget.append('</td>')
        if field.get_value('show_edit_button'):
            widget.append('<td width="24">')
            url = ''
            request = getattr(field, 'REQUEST', None)
            if request:
                model = getattr(request, 'model', None)
                if model and request.has_key('docref'):
                    # we're in an ExternalSource, use the document in which it is
                    # placed instead of the source as the model
                    url = model.resolve_ref(
                        quote(request['docref'])).absolute_url()
            widget.append(
                render_element(
                    'button',
                    name=key + '_editbutton',
                    css_class="kupu-button kupu-link-reference button transporter",
                    title='edit...',
                    onclick="reference.editReference('%s','%s');return false;"%(key,url),
                    contents=render_element(
                        'img',
                        width='16',
                        height='16',
                        src='/silva/globals/edit-find.png'
                    )
                )
            )
            widget.append('</td>')
        widget.append('</tr></table>')
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
