## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
content = node.get_content()
texts = [context.service_editorsupport.render_text_as_html(child) 
            for child in node.childNodes 
            if child.nodeType == node.ELEMENT_NODE and child.nodeName == 'li'
        ]
if node.hasAttribute('type'):
    type = node.getAttribute('type')
else:
    type = 'disc'
return context.util.render_list(type, texts)
