## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
content = node.get_content()

type = None
if node.hasAttribute('type'):
    type = node.getAttribute('type')

# first remove any crap
items = [child for child in node.childNodes if child.nodeType == node.ELEMENT_NODE and (child.nodeName == 'dt' or child.nodeName == 'dd')]

# now we're sure there are only dt's and dd's in the list. split them up into
# pairs
i = 0
pairs = []
while 1:
    if i >= len(items):
        break
    pair = []
    child = items[i]
    if child.nodeName == 'dt':
        pair.append(context.service_editorsupport.render_text_as_html(child))
        nextChild = items[i+1]
        if nextChild.nodeName == 'dd':
            pair.append(context.service_editorsupport.render_text_as_html(
                nextChild))
            pairs.append(pair)
            i += 1
        else:
            # should not happen, a dt without a following dd, but let's allow 
            # it anyway
            pair.append('')
    else:
        # as with the dt following a dt, a dd following a dd should not happen,
        # but let's allow it anyway
        pair = ['', context.service_editorsupport.render_text_as_html(child)]
    i += 1

return context.util.render_dlist(type, pairs)
