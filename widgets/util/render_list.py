## Script (Python) "render_list"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type, texts
##title=
##
model = context.REQUEST.model
type = model.output_convert_html(type)

if type in ['disc', 'square', 'circle']:
    tag = 'ul'
elif type in ['1', 'I', 'i', 'A', 'a']:
    tag = 'ol'
elif type == 'none':
    tag = None

if tag:
    content = ''.join(['<li>%s</li>' % text for text in texts])
    return '<%s class="frontend" type="%s">%s</%s>' % (
        tag, type, content, tag)
else:
    if texts:
        content = '<br />\n'.join(texts)
        return '<span class="li">%s</span>' % content
    else:
        return ''
