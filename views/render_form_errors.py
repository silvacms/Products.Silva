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
    result.append('<li class="error">%s: %s</li>' % (error.field['title'].lower(), error.error_text))

return """
<dl>
<dt>Sorry, errors in form:</dt>
<dd>
<ul class="tips">
%s
</ul>
</dd>
</dl>
""" % (' '.join(result))
