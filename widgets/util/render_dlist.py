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
    content = '<dl class="dl"'
    if type == 'normal':
        content += '>\n'
    else:
        content += ' compact="compact">\n'
    for title, item in pairs:
        content += '<dt>%s</dt>\n  <dd>%s</dd>\n' % (title, item)
    content += '</dl>'
else:
    content = ''

return content
