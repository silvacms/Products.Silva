##parameters=base_path, item_path
# $Id: path_mangler.py,v 1.2 2003/03/19 09:21:18 zagy Exp $
# returns relative path of item_path if the item is in basepath or a subfolder.
# base_path, item_path: tuple
# returns tuple


i = 0
absolute = 0
for i in range(0, min(len(item_path), len(base_path))):
    if item_path[i] != base_path[i]: 
        absolute = 1
        break
if not absolute:
    item_path = item_path[len(base_path):]
return item_path

