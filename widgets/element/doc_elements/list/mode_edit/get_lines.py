## Script (Python) "get_lines"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node

l = 0
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'li':
        text = node.render_text_as_editable(child)
        t = len(text) / 40
        if t == 0:
            t = 1
        l += t
    l += 1
if l < 7:
    return 7
else:
    return l
