## Script (Python) "upgrade_list_titles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=root_id
##title=
##
def update_list_item(node):
   for child in node.childNodes:
       if child.nodeName in ('list', 'nlist'):
          if child.firstChild and child.firstChild.nodeName=='title':
            # update already done 
            print '  update already done for ',child.getNodePath('widget')
            continue
          title = child.getAttribute('title')
          if not title:
            title=''
          child.removeAttribute('title')

          title_el = node.ownerDocument.createElement('title')
          title_text= node.ownerDocument.createTextNode(title)
	  title_el.appendChild(title_text)
          if child.firstChild:
            child.insertBefore(title_el, child.firstChild)
          else:
            child.appendChild(title_el)
          print '  updated list tile of node '+child.getNodePath('widget')
       if child.nodeType == child.ELEMENT_NODE:
          print update_list_item(child),
   return printed

def find_silva_xml_doc(start_point):
    print 'update',start_point.absolute_url(1)
    # print ' ... check for updating: '+','.join(start_point.objectIds())  
    for id, obj in start_point.objectItems():
        if obj.meta_type in ['Silva Folder', 'Silva Publication', 'Silva Root']:
            # print ' step into', id
            print find_silva_xml_doc(obj),
        elif obj.meta_type in ['Silva Document']:
           print 'update document '+obj.absolute_url(1)
           for xml_id, xml in  obj.objectItems():
              if xml.meta_type != 'Parsed XML':
                 print 'XXX Hey, got a version which is not parsed xml:'+id
              else:
                 print '  update version',xml_id
                 print update_list_item(xml.documentElement),
    return printed

root_folder = getattr(context, root_id)
print find_silva_xml_doc(root_folder),

return printed
