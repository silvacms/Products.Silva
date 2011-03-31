from Products.Silva.i18n import translate as _
from zope.i18n import translate

request = context.REQUEST
model = request.model
view = context

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = view.tab_sticky_content_add_form.validate_all(request)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.tab_sticky_content_add(message_type="error",
        message=view.render_form_errors(e))

ssc = model.service_sticky_content.aq_inner

new_result = {'object_path':result['page-asset'],
              'placement':result['placement']}

part = ssc.manage_addStickyContent(new_result,
                                   result['layout'],
                                   result['slot']
                                   )

return view.tab_sticky_content(message_type='feedback',
                               message=_('Sticky Content Service created.'))
