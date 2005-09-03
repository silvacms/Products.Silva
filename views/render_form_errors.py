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
    error_text = error.error_text
    title = error.field['title']
    # if error_text or title is a MessageIDUnicode instance,
    # call it to transform it to
    # a plain string first
    if callable(error_text):
        error_text = error_text()
    if callable(title):
        title = title()
    result.append('<li class="error">%s: %s</li>\n' % 
                    (title, error_text))
return ("""<dl style="margin:0; padding:0.3em 0 0.2em 0;"><dt>""" + 
unicode(_("Sorry, there are problems with these form fields:")) + 
"""</dt><dd><ul class="tips">""" + ' '.join(result) + "</ul></dd></dl>")
