from Products.ParsedXML.ParsedXML import ParsedXML

class XMLImporterError(Exception):
    pass

def importFile(folder, file):
    import_tree = ParsedXML('temp', file.read())
    importInto(folder, import_tree)
    
def importInto(folder, node):
    childNodes = []
    for child in node.childNodes:
        if child.nodeName in ('silva_publication', 'silva_folder', 'silva_document'):
            childNodes.append(child)
       
    for child in childNodes:
        if child.nodeType != node.ELEMENT_NODE:
            continue
        name = child.nodeName
        if name == 'silva_publication':
            id, title = get_id_title(child)
            folder.manage_addProduct['Silva'].manage_addPublication(
                id, title, create_default=0)
            importInto(getattr(folder, id), child)
        elif name == 'silva_folder':
            id, title = get_id_title(child)
            folder.manage_addProduct['Silva'].manage_addFolder(
                id, title, create_default=0)
            importInto(getattr(folder, id), child)
        elif name == 'silva_document':
            id, title = get_id_title(child)
            folder.manage_addProduct['Silva'].manage_addDocument(
                id, title)
            for sub in child.childNodes:
                if sub.nodeName == 'doc':
                    break
            else:
                raise XMLImporterError, "Can't find doc in: %s (%s)" % (name, id)
            version = getattr(getattr(folder, id), '0')
            s = '<?xml version="1.0" encoding="ISO-8859-1" ?>\n' + sub.writeStream().getvalue().encode('latin1')
            version.manage_edit(s)
        else:
            raise XMLImporterError, "Unknown node: %s" % name
        
def get_id_title(node):
    id = str(node.getAttribute('id'))
    # find first element
    for child in node.childNodes:
        if child.nodeName == 'title':
            break
    else:
        raise XMLImporterError, "Can't find title in: %s (%s)" % (node.nodeName, id)
    # get text content of title
    title = (''.join([text_node.data for text_node in child.childNodes])).encode('latin1')
    return id, title

    
