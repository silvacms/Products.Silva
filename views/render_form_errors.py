## Script (Python) "render_form_errors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=validation_error
##title=
##
result = []
for error in validation_error.errors:
    result.append('<li class="error">%s: %s</li>\n' % (error.field['title'], error.error_text))

return """
<dl style="margin:0; padding:0.3em 0 0.2em 0;">
<dt>Sorry, there are problems with these form fields:</dt>
<dd>
<ul class="tips">
%s
</ul>
</dd>
</dl>
""" % (' '.join(result))
