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

# mapping for XHTML compatibility
# disc, square, circle are ok 
# 1 = decimal
# I = upper-roman
# i = lower-roman
# A = upper-alpha
# a = lower-alpha
# the class attribute should get the new mapping 

if tag:
    content = ''.join(['<li>%s</li>\n' % text for text in texts])
    return '<%s class="%s">\n%s</%s>' % (
        tag, type, type, content, tag)
else:
    if texts:
        content = '<br />\n'.join(texts)
        return '<p class="nobullet">\n%s\n</p>' % content
    else:
        return ''
