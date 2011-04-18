# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

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
from Products.Formulator.Validator import StringBaseValidator
from Products.Formulator.Widget import render_element,TextWidget
from Products.Formulator.helpers import is_sequence
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
        ob = self.context.aq_inner.restrictedTraverse(path,None)
        if not ob:
            raise BadRequest("Invalid location.  Unable to redirect to the edit view.")
        if ISilvaObject.providedBy(ob):
            if checkonly == 'y':
                return "valid"
            else:
                request.response.redirect(ob.absolute_url() + '/edit')
                return "redirecting"
        raise BadRequest("Invalid location.  Target must be a Silva Object in order to edit")

class LookupWindowValidator(StringBaseValidator):

    message_names = StringBaseValidator.message_names +\
                  ['exceeded_maxrows', 'required_not_met']

    exceeded_maxrows = 'Too many references.'
    required_not_met = 'Not enough references.'

    def validate(self, field, key, REQUEST):
        #during silva xml import, the REQUEST object is a dictionary,
        # and NOT an IHTTPRequest.  In this case, getPathAdapter will fail
        # with a TypeError.  When this happens use a "dummy" path adapter, which
        # just returns it's own value
        class dummyPAD(object):
            def urlToPath(self, val):
                return val
        try:
            pad = getPathAdapter(REQUEST)
        except TypeError:
            pad = dummyPAD()

        values = REQUEST.get(key, [])
        # NOTE: a hack to deal with single item selections
        if not is_sequence(values):
            # put whatever we got in a list
            values = [values]

        result = []
        for value in values:
            if not field.get_value('whitespace_preserve'):
                value = value.strip()
            res = pad.urlToPath(value)
            if res:
                result.append(res)

        maxrows = field.get_value('max_rows')
        if maxrows > 0 and len(result) > maxrows:
            self.raise_error('exceeded_maxrows',field)
        reqrows = field.get_value('required_rows')
        if reqrows > 0 and len(result) < reqrows:
            self.raise_error('required_not_met',field)
        return ', '.join(result)

class LookupWindowWidget(TextWidget):

    property_names = TextWidget.property_names  + ['onclick','button_label','show_edit_button','show_add_remove','max_rows','required_rows']

    default_onclick_handler = """{
var myid = this.getAttribute('id').replace(/^button/,'input');
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
        if field.field_record:
            key = key.replace(':record',':record:list')
        ret = ['<table class="kupu-link-reference-table">']
        values = value.split(', ')
        reqrows = field.get_value('required_rows')
        if reqrows > 0 and reqrows > len(values):
            #somehow the number of required rows exceeds the number of values, so
            # add some more rows
            values.extend(['' for i in range(len(values),reqrows) ])
        for i,v in enumerate(values):
            ret.extend(self._render_helper(field, key, v, request, str(i)))
        maxrows = field.get_value('max_rows')
        if field.get_value('show_add_remove') and maxrows > len(values):
            ret.append('<tr><td colspan="2" class="buttoncell">')
            ret.append(render_element(
                'button',
                id='addbutton_' + key,
                name='addbutton_' + key,
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
        editid = 'editbutton%s_%s'%(index,key)
        onclick = self._onclick_handler(field, 'input'+index+'_'+key)
        if show_edit:
            onclick += ";document.getElementById(this.getAttribute('id').replace(/^button/,'editbutton'))"

        widget.append('<tr><td class="buttoncell">')
        widget.append(
            render_element(
                'button',
                name='button%s_%s'%(index,key),
                id='button%s_%s'%(index,key),
                css_class="kupu-button kupu-link-reference kupu-link-lookupbutton",
                title=field.get_value('button_label') or 'get reference...',
                onclick="%s;return false;" % onclick,
                contents=' ')
        )
        widget.append('<br/>')
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
                else:
                    url = model.absolute_url()
            widget.append(
                render_element(
                    'button',
                    name=editid,
                    id=editid,
                    css_class="kupu-button kupu-link-reference kupu-link-editbutton",
                    style="display: " + str(len(value) > 0 and "inline" or "none"),
                    title='edit...',
                    onclick="reference.editReference(this.getAttribute('id').replace(/^editbutton/,'input'),'%s');return false;"%(url),
                    contents=' '
                )
            )
            widget.append('<br/>')
        remove_style = ''
        if (not show_add_remove) or (reqrows and reqrows > int(index)):
            remove_style = "display:none"
        if (not show_add_remove) and (not show_edit):
            widget.append('<br/>')
        widget.append(
            render_element(
                'button',
                name='removebutton%s_%s'%(index,key),
                id='removebutton%s_%s'%(index,key),
                css_class='kupu-button kupu-link-reference kupu-link-removebutton',
                title='remove reference...',
                style=remove_style,
                onclick='removeRowFromReferenceLookupWidget(this); return false;',
                contents=' '))
        widget.append('</td><td>')
        widget.append(
            render_element(
                'textarea',
                name=key,
                id='input%s_%s'%(index,key),
                css_class=field.get_value('css_class'),
                rows="2",
                cols="20",
                contents=value))
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
        assert ISilvaObject.providedBy(model)
        interpolate = {
            'url': model.get_container().absolute_url(),
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
