## Script (Python) "render"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.helpers import escape_entities

node = context.REQUEST.node

datasource = context.get_datasource()
parameters = context.get_parameters()

errmsg = "<span class='warning'>[externaldata element broken]</span>"
if not datasource:
    return errmsg

#formerr = context.get_formerror()
#if formerr:
#    return errmsg

try:
    data = datasource.get_data(parameters)
except: 
    return errmsg

# FIXME: Using CSS this hairball is slightly less hairy
# than it used to be
caption = escape_entities(datasource.get_title())
type = node.getAttribute('type') or 'listing'
show_headings = node.getAttribute('show_headings') or 'true'
show_caption = node.getAttribute('show_caption') or 'true'

table_data = []
if show_headings == 'true':
    table_data.append("""<tr class="rowheading">""")
    for name in data.names():
        table_data.append("""<td align="%s">\n  %s\n</td>""" % ('left', name))
    table_data.append("""</tr>""")

rownr = 0
for row in data:
    row_data = []
    col = 0
    for field in row:
        col += 1
        row_data.append(
            """<td align="%s">\n  %s\n</td>""" % ('left', field))        
    rownr += 1
    if rownr % 2: cssclass = "odd"
    else: cssclass = "even"
    table_data.append(
        """<tr class="%s">\n%s\n</tr>""" % (cssclass, '\n'.join(row_data)))

table = []
table.append("""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
if show_caption == 'true':
    table.append("""<caption>%s</caption>""" % (caption))
table.append("""<tbody>""")
table.append('\n'.join(table_data))
table.append("""</tbody>""")
table.append("""</table>""")

return '\n'.join(table) + '\n'
