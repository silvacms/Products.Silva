## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
columns_info = context.get_columns_info()

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = ""
nr_of_columns = len(columns_info)
type = node.getAttribute('type')

table_data = []
for child in node.childNodes:
    if child.nodeType != node.ELEMENT_NODE:
        continue
    if child.nodeName == 'row':
        row_data = []
        col = 0
        for field in child.childNodes:
            if field.nodeType != node.ELEMENT_NODE:
                continue
            if field.nodeName == 'field':
                # get field content
                if context.is_field_simple(field):
                    for p_node in field.childNodes:
                        if p_node.nodeType == node.ELEMENT_NODE:
                            break
                    content = \
                        context.service_editorsupport.render_text_as_html(
                            p_node)
                else:
                    context.service_editor.setViewer('service_sub_previewer')
                    content = context.service_editor.renderView(field)
                # append field content
                if content == '':
                    content = '&nbsp;'
                row_data.append(
                    """<td class="align-%s">\n  %s\n</td>""" % (
                    columns_info[col]['align'], content))
                    # this align thingy should not be needed if mozilla would
                    # consider the alignment as specified in the <col />
                col += 1
        table_data.append(
            """<tr>\n%s\n</tr>""" % '\n'.join(row_data))
    if child.nodeName == 'row_heading':
        table_data.append(
            '<tr class="rowheading">\n<td colspan="%s">\n  %s\n</td>\n</tr>' % (
            nr_of_columns, 
            context.service_editorsupport.render_heading_as_html(child)))

table = []
table.append("""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
# this is always empty in rendered html
# table.append("""<caption>%s</caption>""" % (caption))
for col in columns_info:
    table.append("""<col width="%s" class="align-%s" valign="top"/>""" % (
        col['html_width'], col['align']))
table.append("""<tbody>""")
table.append('\n'.join(table_data))
table.append("""</tbody>""")
table.append("""</table>""")

return '\n'.join(table) + '\n'
