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
datasource = context.get_datasource()
parameters = context.get_parameters()
data = datasource.get_data(parameters)

output_convert = context.output_convert_html

# FIXME: Using CSS this hairball is slightly less hairy
# than is used to be
caption = datasource.get_title_html()
type = 'listing' #node.getAttribute('type')

table_data = []
table_data.append("""<tr class="rowheading">""")
for name in data.names():
    table_data.append("""<td align="%s">\n  %s\n</td>""" % ('left', name))
table_data.append("""</tr>""")

for row in data:
    row_data = []
    col = 0
    for field in row:
        row_data.append(
            """<td align="%s">\n  %s\n</td>""" % ('left', field))
        col += 1
    table_data.append(
        """<tr>\n%s\n</tr>""" % '\n'.join(row_data))

table = []
table.append("""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
table.append("""<caption>%s</caption>""" % (caption))
#for col in columns_info:
#    table.append("""<col width="%s" align="%s" valign="top"/>""" % (
#        col['html_width'], col['align']))
table.append("""<tbody>""")
table.append('\n'.join(table_data))
table.append("""</tbody>""")
table.append("""</table>""")

return '\n'.join(table) + '\n'
