## Script (Python) "render_form_errors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=validation_error
##title=
##
from Products.Silva.i18n import translate as _
from zope.i18n import translate

result = []
request = context.REQUEST
for error in validation_error.errors:
    error_text = error.error_text
    title = error.field['title']

    # translate error_text and title first
    error_text = translate(error_text, context=request)
    title = translate(title, context=request)
    
    result.append('<li class="error">%s: %s</li>\n' % 
                    (title, error_text))

return ("""<dl style="margin:0; padding:0.3em 0 0.2em 0;"><dt>""" + 
translate(_("Sorry, there are problems with these form fields:"),
            context=request) + 
"""</dt><dd><ul class="tips">""" + ' '.join(result) + "</ul></dd></dl>")
