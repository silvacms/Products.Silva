## Script (Python) "render_dlist"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type, pairs
##title=
##
if pairs:
    content = '<dl class="frontend"'
    if type == 'normal':
        content += '>'
    else:
        content += ' compact="compact">'
    for title, item in pairs:
        content += '<dt>%s</dt><dd>%s</dd>' % (title, item)
    content += '</dl>'
else:
    content = ''

return content
