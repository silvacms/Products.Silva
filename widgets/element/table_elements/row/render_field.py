## Script (Python) "render_field"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, info
##title=
##
if context.is_field_simple(node):
    # find p first (FIXME: inefficient)
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            break
    node = child
    if len(node.childNodes) == 0:
        return '<td class="align-%s" width="%s">&nbsp;</td>' % (info['align'], 
            info['html_width'])
    if (len(node.childNodes) == 1 and hasattr(node.childNodes[0], 'data') and 
            len(node.childNodes[0].data.strip()) == 0):
        return '<td class="align-%s" width="%s">&nbsp;</td>' % (info['align'], 
            info['html_width'])
    else:
        return '<td class="align-%s" width="%s">%s</td>' % (info['align'], 
            info['html_width'], 
            context.service_editorsupport.render_text_as_html(node))
else:
    context.service_editor.setViewer('service_sub_previewer')
    content = context.service_editor.renderView(node)
    return '<td class="align-%s" width="%s">%s</td>' % (info['align'],
        info['html_width'], content)
