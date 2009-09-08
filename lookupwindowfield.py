# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt

"""
Thank you Samuel, for having the brilliant idea!

NOTE:  The reference lookup window field and the
 lookup window field are now exactly the same.  
 These are kept for backwards compatibility, but
 both can be used to the same effect.
"""

from urllib import quote
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringValidator
from Products.Formulator.Widget import render_element,TextWidget
from Products.Silva.adapters.path import getPathAdapter
import re

from Products.Five import BrowserView
from urlparse import urlparse
from zExceptions import BadRequest

from interfaces import ISilvaObject

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
    
    message_names = StringValidator.message_names +\
                  ['exceeded_maxrows', 'required_not_met']

    exceeded_maxrows = 'Too many references.'
    required_not_met = 'Not enough references.'

    def validate(self, field, key, REQUEST):
        pad = getPathAdapter(REQUEST)
        keymatch = re.compile(r'^%s\d*?$'%key)
        keys = []
        ret = []
        if not hasattr(REQUEST,'form'):
            # this is from Silva metadata, in which case REQUEST
            # is just the original REQUEST.form dictionary
            f = REQUEST
        else:
            f = REQUEST.form
        for k in f.keys():
            if keymatch.match(k):
                keys.append(k)
        #the keys need to be in order
        keys.sort()
        for k in keys:
            ret.append(pad.urlToPath(StringValidator.validate(self, field, k, REQUEST)))
        maxrows = field.get_value('max_rows')
        if maxrows > 0 and len(ret) > maxrows:
            self.raise_error('exceeded_maxrows',field)
        reqrows = field.get_value('required_rows')
        if reqrows > 0 and len(ret) < reqrows:
            self.raise_error('required_not_met',field)
        return ', '.join(ret)
    
class LookupWindowWidget(TextWidget):
    
    property_names = TextWidget.property_names  + ['onclick','button_label','show_edit_button','show_add_remove','max_rows','required_rows']
    
    default_onclick_handler = """{
var myid = this.getAttribute('id').replace(/_button/,'');
reference.getReference(
    function(path, id, title) {
        document.getElementById(myid).value = path;;
        }, '%(url)s', '', true, '%(selected_path)s')}
        """
    
    onclick = fields.TextAreaField(
        'onclick',
        title='Onclick', 
        description='onclick handler implementation',
        default=default_onclick_handler,
        required=0,
        width='40', 
        height='4')
    
    button_label = fields.StringField(
        'button_label',
        title='Label for get reference button',
        description='The title for the get reference button',
        default='get reference...',
        required=0)
    
    show_edit_button = fields.CheckBoxField(
        'show_edit_button', 
        title='Show edit reference button', 
        description="Adds an 'Edit Reference' button to the widget.  When clicked, this will open a new window and redirect to the edit tab for the reference, if it is a valid Silva relative reference.  NOTE: only works in kupu.",
        required=0,
        default="")

    show_add_remove = fields.CheckBoxField(
        'show_add_remove', 
        title='Show add / remove reference buttons', 
        description="Adds an 'add reference' button to the bottom of this widget and 'remove reference' buttons next to each reference row in the widget.  Only references greater than the number required have the 'remove reference' button.",
        required=0,
        default=True)

    max_rows = fields.IntegerField(
        'max_rows',
        title='Maximum Rows',
        description=(
            "The maximum number of rows allowed for this LookupWindowField."
            " It will not be possible to add more rows beyond this number, and"
            " this is also validated on the server side."),
        default=1,
        required=True)

    required_rows = fields.IntegerField(
        'required_rows',
        title='Required Rows',
        description=(
            "The minimum number of references required for this LookupWindowField."
            " If not set to 0, this essentially makes the field required. [ 0 disables this property ]"
            " This is validated on the server side. The number of required rows must be less than or"
            " equal to the maximum number of rows allowed."),
        default=0,
        required=True)

    def render(self, field, key, value, request):
        ret = ['<table class="kupu-link-reference-table" cellpadding="0" cellspacing="0">']
        values = value.split(', ')
        reqrows = field.get_value('required_rows')
        if reqrows > 0 and reqrows > len(values):
            #somehow the number of required rows exceeds the number of values, so
            # add some more rows
            values.extend(['' for i in range(len(values),reqrows) ])
        for i,v in enumerate(values):
            ret.extend(self._render_helper(field, key, v, request, str(i)))
        if field.get_value('show_add_remove'):
            ret.append('<tr><td colspan="3">')
            maxrows = field.get_value('max_rows')
            ret.append(render_element(
                'button',
                id=key + '_addbutton',
                name=key + '_addbutton',
                css_class='kupu-button kupu-link-reference kupu-link-addadditional',
                title='add additional reference...',
                onclick="addRowToReferenceLookupWidget(this, %s); return false;"%maxrows,
                contents=' ')
                       )
            ret.append('</td></tr>')
        ret.append('</table>')
        return ''.join(ret)

    def _render_helper(self, field, key, value, request, index):
        widget = []
        value = getPathAdapter(field.REQUEST).pathToUrlPath(value)
        show_edit = field.get_value('show_edit_button')
        show_add_remove = field.get_value('show_add_remove')
        reqrows = field.get_value('required_rows')
        editid = '%s_editbutton%s'%(key,index)
        onclick = self._onclick_handler(field, key + index)
        buttoncellstyle=''
        if show_edit:
            onclick += ";document.getElementById(this.getAttribute('id').replace(/_button/,'_editbutton')).style.display='inline';this.parentNode.style.width='42px';"
            if value:
                buttoncellstyle=" style='width:42px'"
                                                                                    
        widget.append('<tr><td class="buttoncell"%s>'%buttoncellstyle)
        widget.append(
            render_element(
                'button',
                name='%s_button%s'%(key,index),
                id='%s_button%s'%(key,index),
                css_class="kupu-button kupu-link-reference kupu-link-lookupbutton",
                title=field.get_value('button_label') or 'get reference...',
                onclick="%s;return false;" % onclick,
                contents=' ')
        )
        if show_edit:
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
                    name=editid,
                    id=editid,
                    css_class="kupu-button kupu-link-reference kupu-link-editbutton",
                    style="display: " + str(len(value) > 0 and "inline" or "none"),
                    title='edit...',
                    onclick="reference.editReference(this.getAttribute('id').replace(/_editbutton/,''),'%s');return false;"%(url),
                    contents=' '
                )
            )
        widget.append('</td><td style="text-align:right; padding-right: 3px;">')
        taid = '%s_inputta%s'%(key,index)
        widget.append(
            render_element(
                'input',
                type='text',
                name=key + index,
                id=key + index,
                css_class=field.get_value('css_class'),
                value=value,
                size=field.get_value('display_width'),
                maxlength=field.get_value('display_maxwidth'),
                onfocus="ta=document.getElementById(this.getAttribute('taid'));this.style.display='none';ta.value=this.value;ta.style.display='inline';ta.focus();",
                taid=taid,
                extra=field.get_value('extra')))
        widget.append(
            render_element(
                'textarea',
                name=taid,
                id=taid,
                key=key + index,
                css_class=field.get_value('css_class'),
                rows="2",
                cols="24",
                onblur="i=document.getElementById(this.getAttribute('key'));i.value=this.value;i.style.display='inline';this.style.display='none';",
                contents=value))
        widget.append('</td><td>')
        remove_style = ''
        if (not show_add_remove) or (reqrows and reqrows > int(index)):
            remove_style = "visibility:hidden"
        widget.append(
            render_element(
                'button',
                name='%s_removebutton%s'%(key,index),
                id='%s_removebutton%s'%(key,index),
                css_class='kupu-button kupu-link-reference kupu-link-removebutton',
                title='remove reference...',
                style=remove_style,
                onclick='removeRowFromReferenceLookupWidget(this); return false;',
                contents=' '))
        widget.append('</td></tr>')
        return widget
    
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

class LookupWindowField(StringField):
   
    meta_type = 'LookupWindowField'
    validator = LookupWindowValidator()
    widget = LookupWindowWidget()

class ReferenceLookupWindowField(StringField):

    meta_type = 'ReferenceLookupWindowField'
    validator = LookupWindowValidator()
    widget = LookupWindowWidget()
    
FieldRegistry.registerField(LookupWindowField)
FieldRegistry.registerField(ReferenceLookupWindowField)
