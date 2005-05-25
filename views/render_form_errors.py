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
result = []
for error in validation_error.errors:
    result.append('<li class="error">%s: %s</li>\n' % 
                    (error.field['title'], error.error_text()))
return ("""<dl style="margin:0; padding:0.3em 0 0.2em 0;"><dt>""" + 
unicode(_("Sorry, there are problems with these form fields:")) + 
"""</dt><dd><ul class="tips">""" + ' '.join(result) + "</ul></dd></dl>")
