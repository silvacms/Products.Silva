## Script (Python) "get_code_elements"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# This script returns a sorted list of available code elements for selection.
# Code elements are scripts or ZPTs residing in folders named 'codecalls'.
# The script looks for such folders starting from the place of the document
# up to the Silva root.
# If a folder 'codecalls' is found on the same level of the document, every
# script or ZPT contained is added to the list.
# However, scripts or ZPTs contained in 'codecalls' folder above the document are
# added only if they're not hidden, i.e. if they are not member of a list returned
# by a script named 'hidden'.
# This functionality allows the site developer to selectively hide some codecalls
# from beeing called by lower level documents.

request = context.REQUEST

items = []
hideOn = 0
hidden = []
for obj in request.PARENTS:
  if obj.meta_type == 'Silva Publication' or obj.meta_type == 'Silva Folder' or obj.meta_type == 'Silva Root':
    if 'codecalls' in obj.objectIds('Folder'):
      for folder in obj.objectValues('Folder'):
        if folder.getId() == 'codecalls':
          if 'hidden' in folder.objectIds('Script (Python)'):
            if hideOn:
              for hiddenItem in folder.hidden():
                hidden.append(folder[hiddenItem])
            hidden.append(folder['hidden'])
          for item in folder.objectValues(['Page Template', 'Script (Python)']):
            context.selectionSort(items, item)
    if not hideOn:
      hideOn = 1

  if obj.meta_type == 'Silva Root':
      break

if not items:
  return '<p>No Code provided which could be selected</p>'

if hidden:
  for hiddenItem in hidden:
    items.remove(hiddenItem)

if not items:
  return '<p>No Code provided which could be selected</p>'

silvaRoot = context.silva_root()
node = request.node
actualCode = node.render_text_as_editable(node)

options = ''
for item in items:
  if item.absolute_url(silvaRoot) == actualCode:
    options += '<option value="%s" selected="selected">%s</option>' % (item.absolute_url(silvaRoot), item.title_or_id())
  else:
    options += '<option value="%s">%s</option>' % (item.absolute_url(silvaRoot), item.title_or_id())

return '<select name="code">' + options + '</select>'
