## Script (Python) "copy_of_render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
output_convert = context.output_convert_html

table_type = node.getAttribute('type')
if table_type not in ['plain', 'listing', 'grid', 'datagrid']:
    table_type = 'plain'

columns_info = context.get_columns_info()
# return to see comlumns_info datastructure:
#return "columns info:", columns_info

after_column_heading = 0

result = []
result.append('<table border="1" rules="all" width="100%">\n')
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'row':
        result.append('<tr valign="top">\n')
        if not after_column_heading:
            tag = 'th'
            after_column_heading = 1
        else:
            tag = 'td'
        i = 0
        for field in child.childNodes:
            if field.nodeType != node.ELEMENT_NODE:
                continue
            info = columns_info[i]
            if field.nodeName in ['field', 'column_heading']:
                if context.is_field_simple(field):
                  for p_node in field.childNodes:
                     if p_node.nodeType == node.ELEMENT_NODE:
                         break
                  result.append('\n<%s class="transparent" align="%s" width="%s">' % (tag, info['align'], info['html_width']))
                  result.append(node.render_text_as_html(p_node))
                  result.append('</%s>\n' % tag)
                else:
                  context.service_editor.setViewer('service_sub_previewer')
                  content = context.service_editor.getViewer().getWidget(field).render()
                  result.append('<%s class="transparent" align="%s" width="%s">' % (tag, info['align'], info['html_width']))
                  result.append(content)
                  result.append('</%s>\n' % tag)
            i += 1
        result.append('</tr>\n')
    elif child.nodeName == 'row_heading':
        result.append('<tr valign="top">\n<th class="transparent" align="left" colspan="%s">' % output_convert(node.getAttribute('columns')))
        result.append(node.render_heading_as_html(child))
        result.append('</th>\n</tr>\n')
result.append('</table>\n')
return ''.join(result)
