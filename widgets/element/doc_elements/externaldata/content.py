from Products.Silva.helpers import escape_entities

node = context.REQUEST.node

datasource = context.get_datasource()
parameters = context.get_parameters()

errmsg = u"<span class='warning'>[externaldata element broken]</span>"
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
# The Silva views expect unicode everywhere, so we create unicode strings
# and decode the external data into unicode too.
caption = escape_entities(datasource.get_title())
data_encoding = datasource.get_data_encoding()
type = node.getAttribute('type') or u'list'
show_headings = node.getAttribute('show_headings') or u'true'
show_caption = node.getAttribute('show_caption') or u'true'

table_data = []
if show_headings == 'true':
    table_data.append(u"""<tr class="rowheading">""")
    for name in data.names():
        table_data.append(u"""<td align="%s">\n  %s\n</td>""" % (u'left', unicode(name, data_encoding, 'replace') ))
    table_data.append(u"""</tr>""")

rownr = 0
for row in data:
    row_data = []
    col = 0
    for field in row:
        if not field:
            field = ''
        col += 1
        row_data.append(
            u"""<td align="%s">\n  %s\n</td>""" % (u'left', unicode(field, data_encoding, 'replace') ))
    rownr += 1
    if rownr % 2: cssclass = u"odd"
    else: cssclass = u"even"
    table_data.append(
        u"""<tr class="%s">\n%s\n</tr>""" % (cssclass, u'\n'.join(row_data)))

table = []
table.append(u"""<table class="silvatable %s" width="100%%" cellspacing="0" cellpadding="3px">""" % (type))
if show_caption == 'true':
    table.append(u"""<caption>%s</caption>""" % (caption))
table.append(u"""<tbody>""")
table.append(u'\n'.join(table_data))
table.append(u"""</tbody>""")
table.append(u"""</table>""")

return (u'\n'.join(table) + u'\n')
