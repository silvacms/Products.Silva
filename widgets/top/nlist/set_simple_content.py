## Script (Python) "set_simple_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, data
##title=
##
# break data into seperate items
items = data.strip().split("\r\n\r\n")
# find containing child paragraph and replace data there
for child in node.childNodes:
    if child.nodeType == node.ELEMENT_NODE:
        break
node.get_content().replace_text(child, items[0])

# if necessary, add new list items
if len(items) > 1:
    doc = node.ownerDocument
    next = node.nextSibling
    for item in items[1:]:
        li = doc.createElement('li')
        p = li.appendChild(doc.createElement('p'))
        node.get_content().replace_text(p, item)
        node.parentNode.insertBefore(li, next)
