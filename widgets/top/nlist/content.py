## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# XXX one _could_ use "renderElements" here 
# if one registers an empty "title" widget instead ... 
# guess that's too fishy, thus do it by hand

node = context.REQUEST.node
editor = context.service_editor
texts = [editor.render(child) for child in node.childNodes if 
         child.nodeType == node.ELEMENT_NODE and child.nodeName == 'li']

# XXX encoding issues debugging here ?
return ''.join(texts)
