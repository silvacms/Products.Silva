## Script (Python) "save_title"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node, title
##title=save title in <title> tag
##
editorsupport = context.service_editorsupport
doc = node.documentElement

title_node = None
for child in node.childNodes:
  if child.nodeName == 'title':
     title_node = child
     break
# fix pathological case of title not the first node
if title_node !=None and title_node != node.firstChild:
  node.insertBefore(title_node, node.firstChild)

# no title found: insert a new one.
if title_node==None:
  title_node = doc.createElement('title')
  node.insertBefore(title_node, node.firstChild)

editorsupport.replace_heading(title_node, title)
