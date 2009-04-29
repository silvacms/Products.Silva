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

if len(validation_error.errors) == 1:

    error = validation_error.errors[0]
    error_text = error.error_text
    title = error.field['title']

    # translate error_text and title first
    error_text = translate(error_text, context=request)
    #in some cases, translate returns None, in which case fallback to non-translated title
    title = translate(title, context=request) or title

    result.append('%s: %s' % (title, error_text))
    return (''.join(result))

else:

    for error in validation_error.errors:
        error_text = error.error_text
        title = error.field['title']
    
        # translate error_text and title first
        error_text = translate(error_text, context=request)
        #in some cases, translate returns None, in which case fallback to non-translated title
        title = translate(title, context=request) or title
    
        result.append('<li class="error">%s: %s</li>\n' %  (title, error_text))

return ("""<dl style="margin:0;"><dt>""" + 
translate(_("Sorry, there are problems with these form fields:"),
            context=request) + 
"""</dt><dd><ul class="tips">""" + ' '.join(result) + "</ul></dd></dl>")
